import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
RESULTS = json.loads((ROOT / "artefactos" / "resultados.json").read_text(encoding="utf-8"))
OUTPUT = ROOT / "informe.pdf"

NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#2C6E9E")
LIGHT_BLUE = colors.HexColor("#EAF1F8")
LIGHT_GRAY = colors.HexColor("#F2F2F2")
DARK_GRAY = colors.HexColor("#444444")

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=21,
    textColor=NAVY,
    spaceAfter=6,
)
subtitle_style = ParagraphStyle(
    "SubtitleCustom",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=DARK_GRAY,
    spaceAfter=10,
)
heading_style = ParagraphStyle(
    "HeadingCustom",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=12.5,
    leading=15,
    textColor=NAVY,
    spaceBefore=5,
    spaceAfter=5,
)
body_style = ParagraphStyle(
    "BodyCustom",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=colors.black,
    spaceAfter=6,
)
small_style = ParagraphStyle(
    "SmallCustom",
    parent=body_style,
    fontSize=8,
    leading=10,
    spaceAfter=3,
)
center_style = ParagraphStyle(
    "CenterCustom",
    parent=small_style,
    alignment=TA_CENTER,
)
header_cell_style = ParagraphStyle(
    "HeaderCellCustom",
    parent=center_style,
    fontName="Helvetica-Bold",
    textColor=colors.white,
)


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9D9D9"))
    canvas.line(0.55 * inch, 0.46 * inch, 7.95 * inch, 0.46 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK_GRAY)
    canvas.drawString(0.55 * inch, 0.28 * inch, "Banco del Altiplano - Proyecto 1")
    canvas.drawRightString(7.95 * inch, 0.28 * inch, f"Página {document.page}")
    canvas.restoreState()


def paragraph(text, style=body_style):
    return Paragraph(text.replace("`", ""), style)


def heading(text):
    return Paragraph(text, heading_style)


def formatted_table(data, widths, font_size=7.8, header=True):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#A6A6A6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    for row in range(1 if header else 0, len(data)):
        if row % 2 == 0:
            commands.append(("BACKGROUND", (0, row), (-1, row), LIGHT_GRAY))
    table.setStyle(TableStyle(commands))
    return table


auc = RESULTS["auc_pr"]
metrics_a = RESULTS["threshold_metrics"]["A"]
metrics_b = RESULTS["threshold_metrics"]["B"]
bet = RESULTS["bet"]
permutation = RESULTS["permutation"]
economics = RESULTS["economics"]
mechanisms = {row["fraud_type"]: row for row in RESULTS["mechanisms"]}

bank_low = economics["B_vs_A_monthly_savings_at_simulated_scale"] * 2000 * 0.001 / RESULTS["fraud_rate"]
bank_high = economics["B_vs_A_monthly_savings_at_simulated_scale"] * 2000 * 0.003 / RESULTS["fraud_rate"]

story = []
story.append(Paragraph("Monitoreo transaccional: detectar lo que el orden revela", title_style))
story.append(
    Paragraph(
        "Informe para el Comité de Riesgos - Banco del Altiplano - Proyecto 1 - Deep Learning 2026",
        subtitle_style,
    )
)
story.append(paragraph("Nina Najera - 231088 &nbsp;&nbsp;&nbsp; José Antón - 221041", small_style))

story.append(heading("Resumen ejecutivo"))
story.append(
    paragraph(
        "Comparamos una línea base basada en variables agregadas con una LSTM que procesa eventos ordenados. "
        "El Modelo B obtiene un AUC-PR de 0.9768 y el Modelo A obtiene 0.9696. La ventaja global es pequeña. "
        "B detecta más fraudes y reduce el costo de prueba de Q54,120 a Q44,160, pero A conserva mejor precisión y F1. "
        "La prueba de permutación corregida muestra una caída absoluta de 0.0301 al alterar solamente el historial. "
        "La evidencia indica que el orden aporta una señal moderada y específica para algunos mecanismos. "
        "Recomendamos un piloto de B en paralelo al sistema actual."
    )
)

story.append(heading("1. Integridad de datos y protocolo temporal"))
story.append(
    paragraph(
        f"Usamos datos sintéticos generados con la semilla fija {RESULTS['seed']}. "
        f"El conjunto contiene {RESULTS['transactions']:,} transacciones de 700 clientes durante 120 días. "
        f"La tasa de fraude es {RESULTS['fraud_rate'] * 100:.2f} por ciento. "
        "El generador se ejecuta dos veces y exige igualdad exacta entre ambas salidas."
    )
)
story.append(
    paragraph(
        "Se simulan tres mecanismos. `escalada` contiene compras pequeñas seguidas por una compra grande. "
        "`rafaga` contiene varias compras pequeñas en distintos comercios y en pocos minutos. "
        "`canal_raro` representa una compra grande en un horario y una categoría poco habituales. "
        "Se esperaba que una ventana corta tuviera dificultades con `canal_raro`."
    )
)
story.append(
    paragraph(
        "Cada muestra termina en la transacción que se clasifica. Contiene siete eventos históricos y la transacción actual. "
        "A recibe ocho variables agregadas causales. B recibe monto, categoría, canal, hora y tiempo desde el evento anterior."
    )
)
split_data = [
    ["Partición", "Muestras", "Uso"],
    ["Entrenamiento", f"{RESULTS['split_counts']['train']:,}", "Ajuste de A y B, escaladores y normalización"],
    ["Validación", f"{RESULTS['split_counts']['val']:,}", "Decisiones, apuesta C y umbrales"],
    ["Prueba", f"{RESULTS['split_counts']['test']:,}", "Una única fase final de evaluación"],
]
story.append(formatted_table(split_data, [1.25 * inch, 1.05 * inch, 4.75 * inch], font_size=8))
story.append(Spacer(1, 5))
story.append(
    paragraph(
        "La división sigue el tiempo. No se mezclan fechas futuras con entrenamiento. Los parámetros de preparación se ajustan solamente con entrenamiento. "
        "Las arquitecturas, la regla de éxito de C y los umbrales se cierran antes de abrir prueba."
    )
)

story.append(PageBreak())
story.append(heading("2. Comparación común entre A y B"))
story.append(
    paragraph(
        "A usa Gradient Boosting sobre agregados. B usa una LSTM de una capa sobre ocho eventos. Ambos producen puntajes continuos y usan las mismas muestras, fechas y horizonte. "
        "AUC-PR es la métrica principal debido al desbalance."
    )
)
comparison_data = [
    ["Modelo", "AUC-PR val", "AUC-PR test", "Umbral", "Precisión", "Exhaustividad", "F1"],
    [
        "A - agregado",
        f"{auc['A_validation']:.4f}",
        f"{auc['A_test']:.4f}",
        f"{metrics_a['umbral']:.2f}",
        f"{metrics_a['precision']:.1%}",
        f"{metrics_a['exhaustividad']:.1%}",
        f"{metrics_a['F1']:.3f}",
    ],
    [
        "B - secuencial",
        f"{auc['B_validation']:.4f}",
        f"{auc['B_test']:.4f}",
        f"{metrics_b['umbral']:.2f}",
        f"{metrics_b['precision']:.1%}",
        f"{metrics_b['exhaustividad']:.1%}",
        f"{metrics_b['F1']:.3f}",
    ],
]
story.append(formatted_table(comparison_data, [1.35 * inch, 0.88 * inch, 0.88 * inch, 0.68 * inch, 0.88 * inch, 1.05 * inch, 0.6 * inch], font_size=7.5))
story.append(Spacer(1, 8))
story.append(Image(str(ROOT / "figs" / "fig1_pr_curves_AB.png"), width=5.5 * inch, height=3.85 * inch))
story.append(
    paragraph(
        "B mejora AUC-PR en 0.0072. En los umbrales elegidos con validación, B alcanza mayor exhaustividad y menor costo. "
        "A produce menos falsos positivos y obtiene mejor precisión y F1. La decisión no depende de una sola métrica."
    )
)
story.append(
    paragraph(
        "La arquitectura de A se eligió por su capacidad para representar relaciones no lineales entre frecuencia, monto y diversidad. "
        "La LSTM se eligió para conservar un estado del historial sin entregar a B los agregados de A."
    )
)

story.append(PageBreak())
story.append(heading("3. Valor del orden - dos pruebas de falsificación"))
story.append(
    paragraph(
        "Prueba 1 - Permutación controlada. Se barajan las siete transacciones históricas de cada muestra. "
        "La transacción actual permanece en la última posición. Así se destruye el orden del historial sin cambiar el evento que se desea clasificar."
    )
)
figures = Table(
    [
        [
            Image(str(ROOT / "figs" / "fig2_permutacion.png"), width=3.35 * inch, height=2.55 * inch),
            Image(str(ROOT / "figs" / "fig3_mecanismo.png"), width=3.65 * inch, height=2.37 * inch),
        ]
    ],
    colWidths=[3.5 * inch, 3.7 * inch],
)
figures.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
story.append(figures)
story.append(
    paragraph(
        f"El AUC-PR de B baja de {permutation['ordered_auc']:.4f} a {permutation['permuted_mean_auc']:.4f}. "
        f"La caída absoluta es {permutation['absolute_drop']:.4f}. El resultado indica que el orden histórico aporta señal, pero su efecto es moderado."
    )
)
story.append(
    paragraph(
        "Prueba 2 - Desempeño por mecanismo. B mejora frente a A en `rafaga` por 0.0151 de AUC-PR. "
        "B queda por debajo de A en `escalada` y `canal_raro`. El monto actual permite que A detecte con facilidad muchos casos de esos dos mecanismos."
    )
)
mechanism_data = [["Mecanismo", "Casos", "AUC-PR A", "AUC-PR B", "Ventaja B"]]
for name in ["escalada", "rafaga", "canal_raro"]:
    row = mechanisms[name]
    mechanism_data.append(
        [name, str(row["n_pos"]), f"{row['AUC_PR_A']:.3f}", f"{row['AUC_PR_B']:.3f}", f"{row['ventaja_B']:+.3f}"]
    )
story.append(formatted_table(mechanism_data, [1.5 * inch, 0.8 * inch, 1.15 * inch, 1.15 * inch, 1.05 * inch], font_size=8))
story.append(Spacer(1, 6))
story.append(
    paragraph(
        "Conclusión: no afirmamos que el orden siempre ayude. La señal adicional se concentra en secuencias rápidas de montos pequeños. "
        "La cantidad reducida de casos de `escalada` y `canal_raro` limita la precisión de sus estimaciones."
    )
)

story.append(PageBreak())
story.append(heading("4. Apuesta del equipo - combinación de A y B"))
story.append(
    paragraph(
        "Hipótesis previa: combinar los puntajes de A y B mejorará AUC-PR porque los agregados y la secuencia capturan señales diferentes. "
        "El control es el mejor modelo individual dentro de cada partición. La apuesta se considera útil si el margen medio es al menos 0.01."
    )
)
bet_data = [
    ["Medida", "Resultado"],
    ["AUC-PR medio del híbrido", f"{bet['hybrid_mean']:.4f}"],
    ["AUC-PR medio del control", f"{bet['control_mean']:.4f}"],
    ["Margen medio", f"{bet['margin_mean']:+.4f}"],
    ["Regla de éxito", "+0.0100"],
    ["Veredicto", "Útil" if bet["success"] else "No concluyente"],
    ["AUC-PR de C en prueba", f"{auc['C_test']:.4f}"],
]
story.append(formatted_table(bet_data, [3.25 * inch, 2.2 * inch], font_size=8.2))
story.append(Spacer(1, 8))
story.append(
    paragraph(
        "El margen medio de 0.0136 supera la regla previa. El veredicto es útil y no se cambia con el resultado de prueba. "
        "C alcanza el mayor AUC-PR final, pero su integración requiere ejecutar A y B. Por ello se conserva como extensión para el Proyecto Final."
    )
)

story.append(heading("5. Decisión económica"))
story.append(
    paragraph(
        "El costo de un fraude no detectado es Q4,200. El costo de bloquear una transacción legítima es Q180. "
        "Los umbrales se seleccionan con validación y se aplican sin ajustes en prueba."
    )
)
economic_table = [
    ["Escenario", "Umbral", "FN", "FP", "Precisión", "Exhaustividad", "F1", "Costo"],
    ["Sin modelo", "-", "242", "0", "-", "0.0%", "-", f"Q{economics['no_model_test_cost']:,.0f}"],
    [
        "Modelo A",
        f"{metrics_a['umbral']:.2f}",
        str(metrics_a["FN"]),
        str(metrics_a["FP"]),
        f"{metrics_a['precision']:.1%}",
        f"{metrics_a['exhaustividad']:.1%}",
        f"{metrics_a['F1']:.3f}",
        f"Q{metrics_a['costo']:,.0f}",
    ],
    [
        "Modelo B",
        f"{metrics_b['umbral']:.2f}",
        str(metrics_b["FN"]),
        str(metrics_b["FP"]),
        f"{metrics_b['precision']:.1%}",
        f"{metrics_b['exhaustividad']:.1%}",
        f"{metrics_b['F1']:.3f}",
        f"Q{metrics_b['costo']:,.0f}",
    ],
]
story.append(formatted_table(economic_table, [1.05 * inch, 0.55 * inch, 0.4 * inch, 0.4 * inch, 0.78 * inch, 0.92 * inch, 0.55 * inch, 1.0 * inch], font_size=7.1))
story.append(Spacer(1, 5))
story.append(Image(str(ROOT / "figs" / "fig4_costo_escenarios.png"), width=4.35 * inch, height=3.05 * inch))

story.append(PageBreak())
story.append(heading("6. Recomendación, errores y límites"))
story.append(
    paragraph(
        "Recomendación: complementar el sistema actual con B durante un piloto en paralelo. B reduce los falsos negativos de 11 a 4 y ahorra Q9,960 frente a A durante 22.48 días de prueba. "
        "A conserva mejor precisión y F1. Por ello no recomendamos un reemplazo inmediato."
    )
)
story.append(
    paragraph(
        f"El ahorro normalizado a treinta días y al mismo tamaño de la simulación es Q{economics['B_vs_A_monthly_savings_at_simulated_scale']:,.0f}. "
        f"Una sensibilidad simple para 1.4 millones de tarjetas y una tasa de fraude entre 0.1 y 0.3 por ciento produce un rango de Q{bank_low / 1_000_000:.1f} a Q{bank_high / 1_000_000:.1f} millones al mes. "
        "Este rango no es un pronóstico. Supone escalamiento lineal y no descuenta infraestructura, revisión humana ni fricción con clientes."
    )
)
story.append(heading("Patrones de error"))
error_data = [
    ["Patrón", "Evidencia", "Implicación"],
    [
        "canal_raro",
        "B obtiene 0.476 y A obtiene 0.988 de AUC-PR",
        "Una secuencia corta no sustituye el perfil histórico del cliente",
    ],
    [
        "escalada",
        "B obtiene 0.717 y A obtiene 0.967 de AUC-PR",
        "El monto actual domina la señal y reduce el valor incremental del orden",
    ],
    [
        "rafaga",
        "B supera a A por 0.015 de AUC-PR",
        "B es más útil cuando ninguna compra individual es extrema",
    ],
]
story.append(formatted_table(error_data, [1.05 * inch, 2.45 * inch, 3.55 * inch], font_size=7.6))
story.append(Spacer(1, 8))
story.append(heading("Condiciones que cambiarían la recomendación"))
story.append(
    paragraph(
        "Mantendríamos solo A si los datos reales muestran pocos fraudes tipo `rafaga`, si el costo operativo de B supera el ahorro o si la precisión baja genera una carga de revisión inaceptable. "
        "Daríamos prioridad a C si su ventaja se repite en datos reales y se define un umbral económico con una validación independiente."
    )
)
story.append(heading("Límites y datos faltantes"))
limits = [
    ["Límite", "Acción necesaria"],
    ["Datos sintéticos y tasa de fraude elevada", "Reentrenar y recalibrar con transacciones reales"],
    ["Ventana fija de ocho eventos", "Evaluar longitudes variables y una regla para poco historial"],
    ["Pocos casos en dos mecanismos", "Ampliar la muestra antes de comparar por mecanismo"],
    ["Sin costos de operación", "Medir revisión humana, infraestructura y fricción con clientes"],
    ["Sin variables de dispositivo o ubicación", "Integrar señales externas con controles de privacidad"],
]
story.append(formatted_table(limits, [2.6 * inch, 4.45 * inch], font_size=8))

story.append(PageBreak())
story.append(heading("7. Matriz de evidencias"))
matrix_data = [
    [
        paragraph("Evidencia", header_cell_style),
        paragraph("Figura o tabla", header_cell_style),
        paragraph("Conclusión", header_cell_style),
        paragraph("Limitación", header_cell_style),
    ],
    [
        paragraph("Integridad de datos", small_style),
        paragraph("Sección 1 y tabla de particiones", small_style),
        paragraph("Generador reproducible, ventanas causales y división temporal", small_style),
        paragraph("Los datos no representan fraude real", small_style),
    ],
    [
        paragraph("Comparación común", small_style),
        paragraph("Sección 2, figura 1 y tabla A contra B", small_style),
        paragraph("B mejora AUC-PR y exhaustividad. A mejora precisión y F1", small_style),
        paragraph("La diferencia de AUC-PR es pequeña", small_style),
    ],
    [
        paragraph("Permutación controlada", small_style),
        paragraph("Sección 3 y figura 2", small_style),
        paragraph("Alterar solo el historial reduce AUC-PR en 0.0301", small_style),
        paragraph("La evidencia del orden es moderada", small_style),
    ],
    [
        paragraph("Prueba por mecanismo", small_style),
        paragraph("Sección 3, figura 3 y tabla por mecanismo", small_style),
        paragraph("La ventaja de B se concentra en `rafaga`", small_style),
        paragraph("Hay 23 casos de `escalada` y 12 de `canal_raro`", small_style),
    ],
    [
        paragraph("Apuesta C", small_style),
        paragraph("Sección 4 y tabla de validación cruzada", small_style),
        paragraph("El margen medio de 0.0136 supera la regla previa", small_style),
        paragraph("C requiere ejecutar los dos modelos base", small_style),
    ],
    [
        paragraph("Decisión económica", small_style),
        paragraph("Sección 5, figura 4 y tabla de costos", small_style),
        paragraph("B ahorra Q9,960 frente a A en prueba", small_style),
        paragraph("Los costos y el volumen son simulados", small_style),
    ],
    [
        paragraph("Recomendación y límites", small_style),
        paragraph("Sección 6 y tablas de errores y límites", small_style),
        paragraph("Pilotear B en paralelo y conservar A como referencia", small_style),
        paragraph("Falta validación real y medición operativa", small_style),
    ],
]
story.append(formatted_table(matrix_data, [1.15 * inch, 1.55 * inch, 2.5 * inch, 1.85 * inch], font_size=7.4))
story.append(Spacer(1, 10))
story.append(
    paragraph(
        "Decisión final: realizar un piloto controlado de B junto al sistema actual. Medir ahorro neto, carga de revisión, calibración y desempeño por mecanismo. "
        "Conservar C como candidato para una evaluación independiente en el Proyecto Final."
    )
)

document = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=letter,
    rightMargin=0.55 * inch,
    leftMargin=0.55 * inch,
    topMargin=0.5 * inch,
    bottomMargin=0.6 * inch,
    title="Monitoreo transaccional: detectar lo que el orden revela",
    author="Nina Najera y José Antón",
)
document.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
