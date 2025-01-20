import pyodbc
import datetime
import os
from Modules.consulta_anses import get_anses_query  # Importando la función del módulo

# Connection function from dbconexion.py
def get_connection():
    drivers = [
        '{ODBC Driver 17 for SQL Server}',
        '{ODBC Driver 13 for SQL Server}',
        '{SQL Server Native Client 11.0}'
    ]
    
    server = 'sql01'
    database = 'Gestion'
    
    for driver in drivers:
        try:
            conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;')
            return conn
        except pyodbc.Error as e:
            print(f"Error with {driver}: {e}")
    
    raise Exception("No available drivers could establish a connection.")

# Function to execute the query and retrieve the result
def fetch_query_results():
    query_setup = """
    USE Aportes;
    IF (OBJECT_ID('tempdb.dbo.#Tabla_Temporal', 'U')) IS NOT NULL
        DROP TABLE #temp6;
    """
    
    query_data = """
    DECLARE @fecha_hace_un_año CHAR(8), @fecha_hoy CHAR(8),
    @mes_ultimo_recibo INT, @año_ultimo_recibo INT;

    SELECT TOP 1 @mes_ultimo_recibo = mes, @año_ultimo_recibo = Año
    FROM aportes 
    WHERE Origen_dato = 1 
    ORDER BY Año DESC, Mes DESC;

    SET @fecha_hace_un_año = REPLACE(CONVERT(VARCHAR(10), DATEADD(YEAR, -1, GETDATE()), 112), '-', '');
    SET @fecha_hoy  = REPLACE(CONVERT(VARCHAR(10), GETDATE(), 112), '-', '');

    -- Aquí va la consulta que devuelve resultados
    SELECT * 
    FROM aportes 
    WHERE Año = @año_ultimo_recibo AND Mes = @mes_ultimo_recibo;
    """

    conn = get_connection()
    cursor = conn.cursor()
    
    # Ejecutar las operaciones que no devuelven resultados
    cursor.execute(query_setup)
    conn.commit()  # Asegurarse de que los cambios se confirmen
    
    # Ejecutar la consulta que devuelve resultados
    cursor.execute(query_data)
    
    # Obtener los resultados de la consulta
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return results

# Function to generate the next file sequence (XXX)
def get_next_file_sequence():
    last_sent_sequence = 200  # Given that the last sent file had sequence 200
    return last_sent_sequence + 1

# Function to generate the filename based on the sequence and current date
def generate_filename():
    sequence = get_next_file_sequence()
    today = datetime.datetime.today()
    day_month = today.strftime("%m%d")
    
    # Generating the filename as ANS4MESA.CHACOXXX.MDDMM.TXT
    filename = f"ANS4MESA.CHACO{sequence:03d}.M{day_month}.TXT"
    return filename

# Function to write the results to a text file encoded in ANSI
def write_to_file(data):
    filename = generate_filename()
    filepath = os.path.join(os.getcwd(), filename)  # Saving to the current working directory

    # Writing to file in ANSI encoding
    with open(filepath, "w", encoding="ansi") as file:
        for row in data:
            if row.pedido is not None:
                file.write(f"{row.pedido.strip()}\n")

    return filepath

# Integrating the full process: query execution, file generation, and saving
def generate_ans_file():
    data = fetch_query_results()
    filepath = write_to_file(data)
    return filepath

# Running the process to generate the file
generated_file_path = generate_ans_file()
print(f"File generated at: {generated_file_path}")
