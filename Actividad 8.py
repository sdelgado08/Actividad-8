import PySimpleGUI as sg
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Funciones de soporte
def cargar_usuarios():
    try:
        with open('usuarios.txt', 'r') as file:
            return [line.strip().split(',') for line in file]
    except FileNotFoundError:
        return []

def guardar_usuario(usuario, contraseña):
    with open('usuarios.txt', 'a') as file:
        file.write(f'{usuario},{contraseña}\n')

def cargar_datos(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def guardar_datos(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)

def verificar_campo_numerico(valor, campo):
    if not valor.isdigit():
        sg.popup_error(f'El campo "{campo}" debe ser numérico.')
        return False
    return True

def mostrar_grafico(eventos, participantes):
    df_participantes = pd.DataFrame(participantes.values())  # Se convierte el diccionario a DataFrame
    fig, ax = plt.subplots()
    if not df_participantes.empty:
        conteo_participantes = df_participantes['Evento'].value_counts()
        conteo_participantes.plot(kind='bar', ax=ax)
        ax.set_title('Participantes por Evento')
        ax.set_xlabel('Eventos')
        ax.set_ylabel('Cantidad')
    return fig

def mostrar_grafico_participantes_tipo(participantes):
    # Gráfico circular: Distribución por tipo de participante
    df = pd.DataFrame(participantes.values())
    if not df.empty:
        tipo_participante = df['tipo_participante'].value_counts()
        fig, ax = plt.subplots()
        tipo_participante.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_title('Distribución por Tipo de Participante')
        ax.set_ylabel('')
        plt.show()

def mostrar_grafico_participantes_evento(participantes):
    # Gráfico de barras: Participantes por evento
    df = pd.DataFrame(participantes.values())
    if not df.empty:
        participantes_evento = df['Evento'].value_counts()
        fig, ax = plt.subplots()
        participantes_evento.plot(kind='bar', ax=ax, color='green')
        ax.set_title('Participantes por Evento')
        ax.set_xlabel('Evento')
        ax.set_ylabel('Cantidad')
        plt.show()

def mostrar_grafico_eventos_fecha(eventos):
    # Gráfico de barras horizontal: Eventos por fecha
    df = pd.DataFrame(eventos.values())
    if not df.empty:
        eventos_fecha = df['fecha'].value_counts()
        fig, ax = plt.subplots()
        eventos_fecha.plot(kind='barh', ax=ax, color='darkgreen')
        ax.set_title('Eventos por Fecha')
        ax.set_xlabel('Cantidad')
        ax.set_ylabel('Fecha')
        plt.show()

# Analizar participantes
def analizar_participantes(eventos, participantes):
   
    participantes_por_evento = {}
    for evento in eventos:
        participantes_por_evento[evento] = {
            p["nombre"] for p in participantes.values() if p["Evento"] == evento
        }

    # Convertir los valores en listas de conjuntos
    eventos_lista = list(participantes_por_evento.values())

    # Participantes que asistieron a todos los eventos
    participantes_todos = set.intersection(*eventos_lista) if eventos_lista else set()

    # Participantes que asistieron al menos a un evento
    participantes_al_menos_uno = set.union(*eventos_lista) if eventos_lista else set()

    # Participantes que asistieron solo al primer evento
    participantes_solo_primero = (
        eventos_lista[0] - set.union(*eventos_lista[1:]) if len(eventos_lista) > 1 else set()
    )

    return participantes_todos, participantes_al_menos_uno, participantes_solo_primero

# Cargar datos iniciales
usuarios = cargar_usuarios()
eventos = cargar_datos('eventos.json')  # Diccionario de eventos
participantes = cargar_datos('participantes.json')  # Diccionario de participantes
configuracion = cargar_datos('configuracion.json') or {}

# Ventana de login
def login_window():
    layout_login = [
        [sg.Text('Usuario'), sg.InputText(key='Usuario')],
        [sg.Text('Contraseña'), sg.InputText(password_char='*', key='Password')],
        [sg.Button('Iniciar Sesión')]
    ]
    return sg.Window('Login', layout_login)

login = login_window()

while True:
    event, values = login.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Iniciar Sesión':
        if [values['Usuario'], values['Password']] in usuarios:
            login.close()
            break
        else:
            sg.popup_error('Usuario o contraseña incorrectos.')

layout_eventos = [
    [sg.Text("Nombre Evento"), sg.InputText(key="EventoNombre"), sg.Text("Lugar"), sg.InputText(key="EventoLugar")],
    [sg.Text("Fecha"), sg.InputText(key="EventoFecha"), sg.Text("Hora"), sg.InputText(key="EventoHora")],
    [sg.Text("Cupo"), sg.InputText(key="EventoCupo")],
    [sg.Button("Agregar Evento", key="AgregarEvento"), sg.Button("Modificar Evento", key="ModificarEvento"), sg.Button("Eliminar Evento", key="EliminarEvento")],
    [sg.Listbox(values=list(eventos.keys()), size=(30, 5), key="ListaEventos", enable_events=True)]
]

layout_participantes = [
    [sg.Text("Evento"), sg.Combo(values=list(eventos.keys()), key="ComboEventos", size=(10, 1)), sg.Text("Nombre"), sg.InputText(key="ParticipanteNombre")],
    [sg.Text("Tipo Documento"), sg.InputText(key="ParticipanteDocumento"), sg.Text("Número de documento"), sg.InputText(key="ParticipanteNumeroDocumento")],
    [sg.Text("Teléfono"), sg.InputText(key="ParticipanteTelefono"), sg.Text("Tipo participante"),
     sg.Combo(values=["Estudiante", "Profesor", "Ayudante"], key="ComboTipoParticipante", size=(15, 1))],
    [sg.Text("Dirección"), sg.InputText(key="ParticipanteDireccion")],
    [sg.Button("Agregar Participante", key="AgregarParticipante"), sg.Button("Modificar Participante", key="ModificarParticipante"), sg.Button("Eliminar Participante", key="EliminarParticipante")],
    [sg.Listbox(values=[p['nombre'] for p in participantes.values()], size=(30, 5), key="ListaParticipantes", enable_events=True)]
]

layout_configuracion = [
    [sg.Checkbox("Validar Aforo al agregar participantes", key="ValidarAforo", default=configuracion.get("ValidarAforo", False))],
    [sg.Checkbox("Solicitar imágenes", key="SolicitarImagenes", default=configuracion.get("SolicitarImagenes", False))],
    [sg.Checkbox("Modificar registros", key="ModificarRegistros", default=configuracion.get("ModificarRegistros", False))],
    [sg.Checkbox("Eliminar Registros", key="EliminarRegistros", default=configuracion.get("EliminarRegistros", False))],
    [sg.Button("Guardar", key="GuardarConfiguracion", size=(10, 1))]
]

layout_analizar = [
    [sg.Button("Analizar Participantes", key="AnalizarParticipantes")],
    [sg.Text("Participantes que fueron a todos los eventos:"), sg.Multiline(size=(40, 5), key="ParticipantesTodos")],
    [sg.Text("Participantes que fueron al menos a un evento:"), sg.Multiline(size=(40, 5), key="ParticipantesAlMenosUno")],
    [sg.Text("Participantes que fueron solo al primer evento:"), sg.Multiline(size=(40, 5), key="ParticipantesSoloPrimero")]
]

layout_graficos = [
    [sg.Button("Distribución de participantes por tipo de participante", key="GraficoTipoParticipante")],
    [sg.Button("Participantes por evento", key="GraficoParticipantesEvento")],
    [sg.Button("Eventos por fecha", key="GraficoEventosFecha")],
]

tab_eventos = sg.Tab("Eventos", layout_eventos)
tab_participantes = sg.Tab("Participantes", layout_participantes)
tab_analizar = sg.Tab("Analizar", layout_analizar)
tab_graficos = sg.Tab("Gráficos", layout_graficos)
tab_configuracion = sg.Tab("Configuración", layout_configuracion)

layout = [
    [sg.TabGroup([[tab_eventos, tab_participantes, tab_analizar, tab_graficos, tab_configuracion]])]
]

window = sg.Window("COP16", layout)

while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED:
        break

    # Agregar Evento
    if event == "AgregarEvento":
        nombre_evento = values["EventoNombre"]
        lugar_evento = values["EventoLugar"]
        fecha_evento = values["EventoFecha"]
        hora_evento = values["EventoHora"]
        cupo_evento = values["EventoCupo"]

        if not all([nombre_evento, lugar_evento, fecha_evento, hora_evento, cupo_evento]):
            sg.popup_error("Todos los campos del evento son obligatorios.")
            continue

        if not verificar_campo_numerico(cupo_evento, "cupo"):
            continue

        if nombre_evento in eventos:
            sg.popup_error(f"El evento '{nombre_evento}' ya existe.")
            continue

        if configuracion.get("SolicitarImagenes", True):
            imagen_evento = sg.popup_get_file("Seleccione una imagen para el evento")
            if not imagen_evento:
                sg.popup_error("Debe adjuntar una imagen para el evento.")
                continue

        eventos[nombre_evento] = {
            "nombre": nombre_evento,
            "lugar": lugar_evento,
            "fecha": fecha_evento,
            "hora": hora_evento,
            "cupo": int(cupo_evento),
            "imagen": imagen_evento if configuracion.get("SolicitarImagenes", True) else None
        }
        guardar_datos('eventos.json', eventos)
        window["ListaEventos"].update(list(eventos.keys()))
        window["ComboEventos"].update(values=list(eventos.keys()))
        sg.popup("Evento agregado exitosamente.")    

    # Modificar Evento
    elif event == "ModificarEvento":
        evento_seleccionado = values["ListaEventos"]
        if evento_seleccionado:
            evento_seleccionado = evento_seleccionado[0]
            evento_original = eventos.get(evento_seleccionado, {})
            
            nuevo_nombre = values["EventoNombre"]
            nuevo_lugar = values["EventoLugar"]
            nueva_fecha = values["EventoFecha"]
            nueva_hora = values["EventoHora"]
            nuevo_cupo = values["EventoCupo"]

            if not all([nuevo_nombre, nuevo_lugar, nueva_fecha, nueva_hora, nuevo_cupo]):
                sg.popup_error("Todos los campos del evento son obligatorios.")
                continue

            if not verificar_campo_numerico(nuevo_cupo, "cupo"):
                continue

            if nuevo_nombre != evento_seleccionado and nuevo_nombre in eventos:
                sg.popup_error(f"El evento '{nuevo_nombre}' ya existe.")
                continue

            eventos[nuevo_nombre] = {
                "nombre": nuevo_nombre,
                "lugar": nuevo_lugar,
                "fecha": nueva_fecha,
                "hora": nueva_hora,
                "cupo": int(nuevo_cupo),
                "imagen": eventos[evento_seleccionado].get("imagen")
            }
            
            if nuevo_nombre != evento_seleccionado:
                eventos.pop(evento_seleccionado)
            
            guardar_datos('eventos.json', eventos)
            window["ListaEventos"].update(list(eventos.keys()))
            window["ComboEventos"].update(values=list(eventos.keys()))
            sg.popup(f"Evento '{evento_seleccionado}' modificado exitosamente.")
        else:
            sg.popup_error("Seleccione un evento para modificar.")

    # Eliminar Evento
    elif event == "EliminarEvento":
        evento_seleccionado = values["ListaEventos"]
        if evento_seleccionado:
            evento_seleccionado = evento_seleccionado[0]
            confirmar = sg.popup_yes_no(f"¿Está seguro de que desea eliminar el evento '{evento_seleccionado}'?")
            if confirmar == "Yes":
                eventos.pop(evento_seleccionado)
                guardar_datos('eventos.json', eventos)
                window["ListaEventos"].update(list(eventos.keys()))
                sg.popup(f"El evento '{evento_seleccionado}' ha sido eliminado.")
        else:
            sg.popup_error("Seleccione un evento para eliminar.")

    # Agregar Participante
    if event == "AgregarParticipante":
        evento_seleccionado = values["ComboEventos"]
        nombre_participante = values["ParticipanteNombre"]
        tipo_documento = values["ParticipanteDocumento"]
        numero_documento = values["ParticipanteNumeroDocumento"]
        telefono = values["ParticipanteTelefono"]
        tipo_participante = values["ComboTipoParticipante"]
        direccion = values["ParticipanteDireccion"]
        
        imagen_participante = None 

        if not all([evento_seleccionado, nombre_participante, tipo_documento, numero_documento, telefono, tipo_participante, direccion]):
            sg.popup_error("Todos los campos son obligatorios.")
            continue

        if not numero_documento.isdigit():
            sg.popup_error("El número de documento debe ser numérico.")
            continue

        if configuracion.get("ValidarAforo", False) and len([p for p in participantes.values() if p["Evento"] == evento_seleccionado]) >= eventos[evento_seleccionado]["cupo"]:
            sg.popup_error("El aforo del evento ya está completo.")
            continue
        
        if configuracion.get("SolicitarImagenes", False): 
            imagen_participante = sg.popup_get_file("Seleccione una imagen para el participante")
        if not imagen_participante:  
            continue
            
        participante_id = str(max(map(int, participantes.keys()), default=0) + 1)
        participantes[participante_id] = {
            "Evento": evento_seleccionado,
            "nombre": nombre_participante,
            "tipo_documento": tipo_documento,
            "numero_documento": numero_documento,
            "telefono": telefono,
            "tipo_participante": tipo_participante,
            "direccion": direccion,
            "imagen": imagen_participante
        }
        
        guardar_datos('participantes.json', participantes)
        window["ListaParticipantes"].update([p["nombre"] for p in participantes.values()])
        sg.popup(f"Participante '{nombre_participante}' agregado exitosamente.")

    # Modificar Participante
    elif event == "ModificarParticipante":
        participante_seleccionado = values["ListaParticipantes"]
        if participante_seleccionado:
            participante_nombre = participante_seleccionado[0]
            participante_id = next((k for k, v in participantes.items() if v["nombre"] == participante_nombre), None)
            if participante_id:
                evento_seleccionado = values["ComboEventos"]
                nuevo_nombre = values["ParticipanteNombre"]
                nuevo_tipo_documento = values["ParticipanteDocumento"]
                nuevo_numero_documento = values["ParticipanteNumeroDocumento"]
                nuevo_telefono = values["ParticipanteTelefono"]
                nuevo_tipo_participante = values["ComboTipoParticipante"]
                nueva_direccion = values["ParticipanteDireccion"]

                if not all([evento_seleccionado, nuevo_nombre, nuevo_tipo_documento, nuevo_numero_documento, nuevo_telefono, nuevo_tipo_participante, nueva_direccion]):
                    sg.popup_error("Todos los campos son obligatorios.")
                    continue

                if not nuevo_numero_documento.isdigit():
                    sg.popup_error("El número de documento debe ser numérico.")
                    continue

                for k, participante in participantes.items():
                    if participante["numero_documento"] == nuevo_numero_documento and k != participante_id:
                        sg.popup_error("Ya existe un participante con este número de documento.")
                        break
                else:
                    participantes[participante_id] = {
                        "Evento": evento_seleccionado,
                        "nombre": nuevo_nombre,
                        "tipo_documento": nuevo_tipo_documento,
                        "numero_documento": nuevo_numero_documento,
                        "telefono": nuevo_telefono,
                        "tipo_participante": nuevo_tipo_participante,
                        "direccion": nueva_direccion,
                        "imagen": participantes[participante_id].get("imagen")
                    }
                    guardar_datos('participantes.json', participantes)
                    window["ListaParticipantes"].update([p["nombre"] for p in participantes.values()])
                    sg.popup(f"Participante '{participante_nombre}' modificado exitosamente.")
            else:
                sg.popup_error("No se encontró el participante seleccionado.")
        else:
            sg.popup_error("Seleccione un participante para modificar.")

    # Eliminar Participante
    elif event == "EliminarParticipante":
        participante_seleccionado = values["ListaParticipantes"]
        if participante_seleccionado:
            participante_nombre = participante_seleccionado[0]
            participante_id = next((k for k, v in participantes.items() if v["nombre"] == participante_nombre), None)
            if participante_id:
                confirmar = sg.popup_yes_no(f"¿Está seguro de que desea eliminar al participante '{participante_nombre}'?")
                if confirmar == "Yes":
                    participantes.pop(participante_id)
                    guardar_datos('participantes.json', participantes)
                    window["ListaParticipantes"].update([p["nombre"] for p in participantes.values()])
                    sg.popup(f"El participante '{participante_nombre}' ha sido eliminado.")
            else:
                sg.popup_error("No se encontró el participante seleccionado.")
        else:
            sg.popup_error("Seleccione un participante para eliminar.")
            
    # Analizar Participantes
    elif event == "AnalizarParticipantes":
        participantes_todos, participantes_al_menos_uno, participantes_solo_primero = analizar_participantes(eventos, participantes)
        window["ParticipantesTodos"].update("\n".join(participantes_todos))
        window["ParticipantesAlMenosUno"].update("\n".join(participantes_al_menos_uno))
        window["ParticipantesSoloPrimero"].update("\n".join(participantes_solo_primero)) 
            
    if event == "GraficoTipoParticipante":
        mostrar_grafico_participantes_tipo(participantes)

    elif event == "GraficoParticipantesEvento":
        mostrar_grafico_participantes_evento(participantes)

    elif event == "GraficoEventosFecha":
        mostrar_grafico_eventos_fecha(eventos)
            
    # Guardar configuración
    if event == "GuardarConfiguracion":
        configuracion = {
            "ValidarAforo": values["ValidarAforo"],
            "SolicitarImagenes": values["SolicitarImagenes"],
            "ModificarRegistros": values["ModificarRegistros"],
            "EliminarRegistros": values["EliminarRegistros"]
        }
        guardar_datos('configuracion.json', configuracion)
        sg.popup("Configuración guardada exitosamente.")
    

window.close()