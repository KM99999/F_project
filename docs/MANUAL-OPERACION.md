# Manual de operación — Sistema de Verificación de Recibos

Guía de uso del sistema para el operador. Acompaña al
[Documento de entrega](ENTREGA-M1.md).

---

## 1. Acceso

1. Abrí en el navegador: **`http://66.94.107.182:8080`**
   (o el dominio configurado, cuando se active HTTPS).
2. Ingresá tu **usuario** y **contraseña**.
3. Llegás a la pantalla principal con dos secciones: **Carga** y **Lista**.

> Si no recordás la contraseña, el administrador puede emitir una nueva
> (función de gestión de usuarios).

---

## 2. Nueva verificación (cargar recibo + carnet)

Cada verificación agrupa **dos documentos**: el recibo y el carnet/identidad del
cliente.

1. Entrá a **Carga** (o el botón **+ Nueva verificación**).
2. Subí el **1) Recibo** (arrastrando el archivo o haciendo clic para elegirlo;
   también podés tomar la foto con el celular).
3. Subí el **2) Carnet del cliente** de la misma forma.
4. Tocá **Procesar verificación**.
5. El sistema clasifica el documento, **extrae los datos con IA** y los muestra.
   Al terminar, podés ir al **detalle** del resultado.

**Formatos aceptados:** fotos (incluye HEIC de iPhone), imágenes grandes (se
ajustan solas) y **PDF** (incluso manuscritos).

---

## 3. Lista de recibos

La pantalla **Lista** muestra todas las verificaciones procesadas.

- **Columnas:** fecha del servicio, fecha de proceso, cliente, código del carnet,
  emisor, monto, concepto, estado y score.
- **Estados (color):**
  - 🟢 **Único** — no se detectó duplicado.
  - 🟡 **Posible duplicado** — requiere revisión humana.
  - 🔴 **Duplicado confirmado** — coincide con otro recibo.
- **🚩 Bandera roja** junto al cliente: el nombre del recibo **no coincide** con el
  del carnet → revisar manualmente.
- **Filtros:** por **estado** y por **rango de fechas** (formato `DD/MM/AAAA`).
- Hacé clic en una fila para abrir el **detalle**.

---

## 4. Detalle de una verificación

- **Documento (izquierda):** imagen o **visor de PDF** del recibo. Clic para
  abrirlo en grande / en otra pestaña.
- **Datos extraídos (derecha):** fecha del servicio, fecha de procesamiento, monto,
  cliente, emisor, concepto, forma de pago y score de coincidencia.
- **Carnet del cliente:** código, nombre, fecha de nacimiento e imagen del carnet.
- **Alerta de nombre:** si el nombre del recibo no coincide con el del carnet,
  aparece un aviso rojo para verificación manual.
- **Casos similares:** otros recibos parecidos, con su motivo de coincidencia.

---

## 5. Revisión humana (posibles duplicados)

Cuando un recibo queda como **🟡 Posible duplicado**, en su detalle aparecen dos
botones:
- **Confirmar duplicado** → lo marca como Duplicado confirmado (🔴).
- **Marcar como único** → lo marca como Único (🟢).

Así, ningún caso dudoso se decide automáticamente: siempre lo valida una persona.

---

## 6. Reprocesar un recibo

Si un recibo se cargó antes de una mejora o salió con datos incompletos, podés
volver a procesarlo **sin re-subirlo**:

1. Abrí el **detalle** del recibo.
2. Tocá **🔄 Reprocesar**.
3. El sistema vuelve a leer el documento ya guardado, actualiza los datos y
   recalcula la detección de duplicados.

---

## 7. Exportar a Excel

1. En la pantalla **Lista**, tocá **Exportar a Excel**.
2. Se descarga un archivo `.xlsx` con:
   - Hoja **Recibos**: todos los campos, con la fecha y el monto en su formato
     correcto y un enlace a la imagen de cada recibo.
   - Hoja **Resumen**: totales por estado.

---

## 8. Glosario rápido

- **Score de coincidencia (0–100):** qué tan parecido es un recibo a otro ya
  cargado. Mayor score = mayor probabilidad de duplicado.
- **Único / Posible duplicado / Duplicado confirmado:** estado del recibo según la
  detección y la revisión humana.
- **Código (carnet):** identificador del cliente tomado de su carnet.
