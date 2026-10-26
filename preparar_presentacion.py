"""Presentación en PDF a partir de resultados experimentales verificados."""
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfgen import canvas

RAIZ = Path(__file__).resolve().parent
ANCHO, ALTO = 960, 540
TINTA = colors.HexColor('#18364A')
GRIS = colors.HexColor('#405161')
AZUL = colors.HexColor('#007F92')


def json_archivo(ruta):
    return json.loads((RAIZ / ruta).read_text(encoding='utf-8'))


def csv_archivo(ruta):
    with (RAIZ / ruta).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


class Presentacion:
    def __init__(self, ruta):
        self.pdf = canvas.Canvas(str(ruta), pagesize=(ANCHO, ALTO), pageCompression=1)
        self.pdf.setTitle('Text-to-SQL con QLoRA')
        self.pdf.setAuthor('Nina Nájera y Alejandro Antón')
        self.numero = 0

    def pagina(self, titulo, fuente=None, tam_titulo=34):
        if self.numero:
            self.pdf.showPage()
        self.numero += 1
        self.pdf.setFillColor(TINTA)
        self.pdf.setFont('Helvetica-Bold', tam_titulo)
        self.pdf.drawString(62, 474, titulo)
        self.pdf.setFillColor(GRIS)
        self.pdf.setFont('Helvetica', 12)
        self.pdf.drawRightString(900, 25, str(self.numero))
        if fuente:
            self.pdf.drawString(62, 25, fuente)

    def texto(self, texto, y, ancho=830, tam=22, negrita=False, color=GRIS):
        estilo = ParagraphStyle('texto', fontName='Helvetica-Bold' if negrita else 'Helvetica',
                                fontSize=tam, leading=tam * 1.35, textColor=color)
        p = Paragraph(texto, estilo)
        _, alto = p.wrap(ancho, ALTO)
        if y - alto < 48:
            raise ValueError(f'Texto fuera de página en diapositiva {self.numero}')
        p.drawOn(self.pdf, 64, y - alto)
        return y - alto

    def tabla(self, filas, y, anchos, tam=20, padding=10):
        estilo = ParagraphStyle('celda', fontName='Helvetica', fontSize=tam,
                                leading=tam * 1.2, textColor=TINTA)
        datos = [[Paragraph(escape(str(c)), estilo) for c in fila] for fila in filas]
        tabla = Table(datos, colWidths=anchos, hAlign='LEFT')
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EAF2F4')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, AZUL),
            ('LINEBELOW', (0, 1), (-1, -1), .4, colors.HexColor('#CCD6DA')),
            ('TOPPADDING', (0, 0), (-1, -1), padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        _, alto = tabla.wrap(ANCHO, ALTO)
        if y - alto < 48:
            raise ValueError(f'Tabla fuera de página en diapositiva {self.numero}')
        tabla.drawOn(self.pdf, 64, y - alto)
        return y - alto


def curva_comparada():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 18, 'axes.labelsize': 18,
                         'xtick.labelsize': 17, 'ytick.labelsize': 17, 'legend.fontsize': 18})
    fig, ax = plt.subplots(figsize=(12, 4))
    for nombre, color in [('lora_r8', '#007F92'), ('lora_r16', '#C76035')]:
        filas = csv_archivo(f'resultados/{nombre}/loss.csv')
        ax.plot([int(r['paso']) for r in filas], [float(r['loss']) for r in filas],
                label=nombre.replace('lora_r', 'Rango '), color=color, linewidth=1.6,
                linestyle='--' if nombre == 'lora_r16' else '-')
    ax.set(xlabel='Paso de optimización', ylabel='Loss sobre SQL')
    ax.legend(frameon=False)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    ruta = RAIZ / 'resultados/comparacion_loss.png'
    fig.savefig(ruta, dpi=180)
    plt.close(fig)
    return ruta


def main():
    resumen = json_archivo('resultados/resumen_resultados.json')
    seleccion = json_archivo('resultados/seleccion.json')
    configs = [json_archivo(f'resultados/{n}/resumen.json') for n in ['lora_r8', 'lora_r16']]
    if not all(c['entrenamiento_completo'] for c in configs):
        raise ValueError('Los experimentos no alcanzaron el presupuesto registrado')
    final = resumen['validacion_propia']
    prediccion = resumen['prediccion_oculta']
    contrato = json_archivo('resultados/contrato_inferencia.json')
    d = Presentacion(RAIZ / 'presentacion.pdf')

    d.pagina('Text-to-SQL con QLoRA', tam_titulo=44)
    d.texto('Generación de consultas MySQL<br/>a partir de preguntas en español', 366, tam=32, negrita=True)
    d.texto('Qwen2.5-Coder-0.5B-Instruct', 240, tam=24, color=AZUL)
    d.texto('Nina Nájera · Alejandro Antón<br/>Deep Learning · Universidad del Valle de Guatemala', 170, tam=21)

    d.pagina('Contrato de inferencia', 'Fuente: solucion.py, config.json')
    y = d.texto('Se recibe el esquema completo de la base y una pregunta en español. Se devuelve una sola consulta SELECT o WITH SELECT.', 416)
    y = d.texto('<b>Generación:</b> determinista, sin APIs externas para producir la consulta.', y - 28)
    y = d.texto('<b>Límites:</b> 300 segundos para cargar el modelo y 30 segundos por pregunta.', y - 28)
    d.texto('<b>Motor:</b> MySQL 8.4.10 con ONLY_FULL_GROUP_BY activo.', y - 28)

    d.pagina('Dataset y separación por esquema', 'Fuente: datos/reporte_datos.json, datos/validacion/preguntas.jsonl')
    y = d.texto('Se aceptaron 3,023 pares de 3,102 candidatos. Se descartaron 75 consultas con resultado vacío y 4 con más de 500 filas.', 419, tam=21)
    y = d.tabla([['Nivel', 'Entrenamiento', 'Validación'], ['Fácil', '1,086', '12'],
                 ['Medio', '891', '14'], ['Difícil', '1,046', '14']], y - 18, [300, 265, 265], tam=20)
    d.texto('Entrenamiento: 10 dominios, con nombres completos y abreviados.<br/>Validación: hotel y fútbol, sin presencia en entrenamiento.', y - 20, tam=19)

    d.pagina('Exactitud por ejecución', 'Fuente: evaluador.py, resultados/oraculo.json')
    y = d.texto('La comparación utiliza los resultados de ejecutar el SQL, en lugar de exigir el mismo texto que la referencia.', 416)
    y = d.texto('<b>EX = suma de pesos acertados / suma de pesos</b><br/>Fácil: 1 · Medio: 2 · Difícil: 3 · Peso total: 82', y - 28, color=AZUL)
    y = d.texto('El orden cuenta cuando se solicita. Los números se redondean a dos decimales y se permiten columnas adicionales.', y - 28)
    d.texto('La prueba con las referencias alcanzó EX 1.000. Ese valor comprueba el evaluador y no representa al modelo.', y - 28, tam=19)

    d.pagina('Comparación controlada de QLoRA', 'Fuente: experimentos.md, resultados/lora_r8/resumen.json, resultados/lora_r16/resumen.json')
    filas = [['Factor', 'Rango 8', 'Rango 16'],
             ['Parámetros entrenables', f"{configs[0]['parametros_entrenables']:,}", f"{configs[1]['parametros_entrenables']:,}"],
             ['Pasos / ejemplos procesados', '76 / 304', '76 / 304'],
             ['Tiempo de entrenamiento', f"{configs[0]['segundos_entrenamiento']/60:.1f} min", f"{configs[1]['segundos_entrenamiento']/60:.1f} min"],
             ['Base y precisión', 'NF4 / FP16', 'NF4 / FP16']]
    y = d.tabla(filas, 423, [360, 235, 235], tam=19)
    d.texto('Hipótesis previa: el rango 16 puede representar más relaciones; el rango 8 puede reducir el sobreajuste. Se mantienen alpha 16, dropout 0.05, módulos q_proj/v_proj y tasa 0.0002.', y - 24, tam=19)

    d.pagina('Curvas de entrenamiento', 'Fuente: resultados/lora_r8/loss.csv, resultados/lora_r16/loss.csv')
    d.pdf.drawImage(str(curva_comparada()), 60, 145, width=840, height=280, preserveAspectRatio=True, mask='auto')
    d.texto('La pérdida se calcula solo sobre la respuesta SQL. Los ejemplos cambian entre pasos, por lo que las curvas no tienen que ser monótonas.', 123, tam=20)

    d.pagina('Resultados en validación propia', 'Fuente: resultados/resumen_resultados.json')
    filas = [['Configuración', 'Aciertos', 'EX', 'Máximo (s)']]
    for nombre, etiqueta in [('baseline', 'Base NF4'), ('lora_r8', 'QLoRA rango 8'), ('lora_r16', 'QLoRA rango 16'),
                             ('reparacion', 'Adapter + reparación'), ('validacion_propia', 'Selección final')]:
        r = resumen[nombre]
        filas.append([etiqueta, f"{r['aciertos']}/40", f"{r['ex']:.3f}", f"{r['tiempo_maximo_s']:.2f}"])
    y = d.tabla(filas, 423, [350, 150, 150, 180], tam=19)
    d.texto(f"Se seleccionó {seleccion['adapter'].replace('lora_r', 'rango ')}. La reparación {'se activó' if seleccion['reparar'] else 'se mantuvo desactivada'} para la entrega.", y - 24, tam=20)

    d.pagina('Experimento de reparación', 'Fuente: resultados/seleccion.json, resultados/reparacion.csv')
    y = d.texto('Se mantiene el adapter seleccionado y se activa la corrección de identificadores y de errores de ejecución.', 416)
    y = d.tabla([['Inferencia', 'EX ponderada'], ['Sin reparación', f"{seleccion['ex_original']:.3f}"],
                 ['Con reparación', f"{seleccion['ex_reparacion']:.3f}"]], y - 22, [560, 270], tam=22)
    d.texto('Se permiten dos ejecuciones de diagnóstico y un presupuesto conjunto de 25 segundos. Una consulta ejecutable puede seguir teniendo errores de significado.', y - 25, tam=21)

    d.pagina('Análisis de errores', 'Fuente: resultados/validacion_propia.csv, resultados/revision_errores.csv')
    errores = sorted(final['errores'].items(), key=lambda p: (-p[1], p[0]))
    filas = [['Categoría', 'Cantidad']] + [[k, v] for k, v in errores]
    if not errores:
        filas.append(['Sin errores', '0'])
    y = d.tabla(filas, 422, [640, 190], tam=18, padding=6)
    d.texto('Se distingue entre fallos de ejecución y consultas ejecutables con resultados incorrectos. La revisión de casos conserva la categoría automática y su explicación.', y - 22, tam=19)

    d.pagina('Verificación de inferencia', 'Fuente: resultados/contrato_inferencia.json')
    y = d.texto(f"Tiempo de carga medido: <b>{contrato['carga_segundos']:.2f} segundos</b>.", 416)
    filas = [['Caso', 'Determinista', 'Solo lectura', 'Máximo (s)']]
    for r in contrato['casos']:
        filas.append([r['id'], 'Sí' if r['determinista'] else 'No', 'Sí' if r['solo_lectura'] else 'No', f"{max(r['tiempos_segundos']):.2f}"])
    y = d.tabla(filas, y - 24, [170, 230, 230, 200], tam=21)
    d.texto('Las mediciones corresponden a la GPU local MX350. No acreditan una ejecución en Colab T4.', y - 28, tam=21)

    d.pagina('Predicción de generalización', 'Fuente: resultados/analisis.md, resultados/resumen_resultados.json')
    y = d.texto(f"EX oculta estimada: <b>{prediccion['ex_estimada']:.2f}</b><br/>EX propia observada: {final['ex']:.3f}", 416, tam=30, color=AZUL)
    y = d.texto('Se aplica un descuento relativo heurístico del 20% por la generación con plantillas, la validación en solo dos dominios y la selección sobre ese mismo conjunto.', y - 28, tam=22)
    d.texto('Se procesaron 304 ejemplos del corpus de 3,023 pares. La cobertura limitada y las redacciones repetidas pueden reducir el rendimiento en esquemas y preguntas desconocidos.', y - 28, tam=22)
    d.pdf.save()
    print(f'Presentación generada: {d.numero} diapositivas')


if __name__ == '__main__':
    main()
