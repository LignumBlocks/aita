# HANDOFF 2026-09-26 · Serie «Un mensaje para…» en formato cocina + estrategia de influencer IA

Sesión del 25 al 26 de septiembre de 2026 (sesión de Claude Code en la nube, repo `LignumBlocks/aita`,
rama `claude/tender-hamilton-f2otfk`). Tuvo dos frentes que **no se mezclan**:

- **Frente A — Umbralio** (lo vivo): una serie nueva de video, «Un mensaje para…», hecha con IA en
  formato «cocinando mientras explica». Ya hay dos clips generados. **Es lo que sigue.**
- **Frente B — Proyecto aparte de influencer IA** (nada que ver con Umbralio): análisis del video de
  Mark Tilbury y un plan. En pausa.

---

## 0 · Qué leer, en este orden

1. § 1 (estado en una tabla) y § 2 (lo que decidió Nelson).
2. § 4 (el guion del episodio 1 con sus números) y § 5 (el formato cocina).
3. § 6 (los assets e IDs) y § 7 (qué falta decidir).
4. El resto es contexto y fuentes.

---

## 1 · Estado

| | |
|---|---|
| Serie | «Un mensaje para…». Episodio 1: **«Un mensaje para los que pagan más de $2,000 de renta»** |
| Formato elegido | Nelson (su avatar de IA) **haciendo el desayuno en una cocina real** mientras explica, como el anuncio de Splitero (§ 5). Números y textos se queman en edición |
| Clip 1 (gancho, aguacate, 5 s) | Generado. **Nelson: «Video bien».** Voz: su clon `nelson-voz-v3` por ElevenLabs |
| Bloque de los huevos (la trampa de la cuota, 17 s) | Generado con su voz real de El Claxon como referencia de tono. **Pendiente de la revisión de Nelson** (4 puntos, § 7) |
| Storyboards de B-roll (2 opciones) | **Rechazados**: «demasiado IA, demasiado pulido» |
| Créditos de Higgsfield gastados en la sesión | ~83 (saldo al empezar: 4,959.5; plan Ultra) |
| Nada se tocó en `LignumBlocks/umbralio.com` | Solo lectura (docs, motor, Supabase `settings`) |

---

## 2 · Decisiones de Nelson en esta sesión (valen para lo que siga)

1. **Nada real por ahora.** Ni cara ni calle de verdad. «La discusión no es IA o real: es cuál es el mejor
   contenido si lo hago con IA.» No volver a proponer grabar en persona.
2. **Lo que frena a Nelson de salir en cámara** es exponerse ante la gente y el miedo escénico, no el
   tiempo ni cómo se ve.
3. **Su voz sí:** puede grabar su voz. Para las pruebas acepta la voz que genera el modelo con su audio
   real como referencia de tono.
4. **Todo lo que se ve lo genera la IA.** En edición solo se queman números, textos y subtítulos. «No
   puede ser un video cuya fuerza esté en la edición.»
5. **Fuera los B-rolls de IA pulidos** (maquetas, balanzas, sobres en estudio): «demasiado IA».
6. **El formato bueno es el de Splitero:** una persona haciendo una tarea real en una cocina vivida,
   explicando en serio, con capas de texto. «No diseñes: busca lo que está probado.»
7. **La serie «Un mensaje para…»** le gusta: rápida de hacer y directa. «No estamos fingiendo, vamos
   al grano.»
8. **Entender todo como «para dummies»:** un número a la vez, palabras sencillas.
9. **Umbralio no se mezcla con el proyecto de influencer IA** (Frente B).

---

## 3 · Por qué se llegó aquí (el razonamiento, corto)

- **El cuello de botella de Umbralio no es el alcance.** Pauta del 24-sep: 16 llegadas a `/es/score`,
  0 arranques del cuestionario, 0 leads (`docs/reportes-pauta/2026-09-25.md` en umbralio.com). Hasta el
  6-sep: 5 leads, los 5 fríos (`docs/TICKET_2026-09-06_TODOS-LOS-LEADS-SON-FRIOS.md`). El contenido tiene
  que **filtrar con números** para que entre quien sí puede comprar.
- **La entrevista de calle con IA (Fichas A/B) se puso en pausa:** su gracia es parecer real y ahí la
  IA pierde (el 25-sep: 3 clips rechazados, voces planas, «Hialeah» mal dicho, 169 créditos sin pieza).
- **La mejor señal propia ya existía:** EL MENSAJE (avatar de Nelson hablándole directo a una persona
  específica) sacó **10.24% de CTR**, cuatro veces los otros anuncios (muestra chica).
- **Contexto de plataformas en 2026** (verificado en la sesión): YouTube dejó de pagar a personajes de IA
  que se presentan como expertos en salud/finanzas/leyes/política (16-jul-2026); TikTok prueba detectar
  cuentas de IA en finanzas/salud/política (10-jul-2026); Instagram quita recomendaciones a perfiles de
  IA sin etiqueta (31-ago-2026). **Regla:** etiquetar como IA, y que sea el avatar de una persona real
  con licencia (Nelson) diciendo información con fuente, nunca un «experto» inventado.

---

## 4 · El episodio 1 — guion «para dummies» (versión vigente)

**Números del motor de Umbralio** (`src/lib/tasa-guias.ts` → `cuotaVivienda`): FHA 3.5% de entrada,
tasa FHA **6.952%** (FRED, `settings.rate_fha_30`, fecha 2026-09-24), impuesto 2%, seguro de condo
$2,801/año (OIR), MIP 0.55%, sin cuota de asociación salvo donde se indica. Precio típico de condo:
$408,000 (MIAMI REALTORS, agosto 2026). **Recalcular el día que se grabe: la tasa cambia a diario.**

| Cifra | Valor | Cómo sale |
|---|---|---|
| $2,200/mes compra un condo de | **~$231,000** | sin asociación |
| Cada $100 de cuota de asociación | **−$11,767** de precio | ~$12,000 en el guion |
| Con $300 de cuota | **~$196,000** | |
| Condo típico ($408K) | **~$3,700/mes** | sin asociación |
| Para entrar (condo de ~$231K) | **$13,860–$19,635** | 3.5% + cierre 2.5–5% (motor). ⚠ El cuestionario suma además un colchón de $5K–$10K |
| Ayuda de Miami-Dade (PHCD) | **hasta $35,000**, 0%, sin cuota, se devuelve al vender; aportas el 1% (~$2,300) | `_content/programas.ts`, verificado 2026-08-30. Requisitos: primera vivienda, límite 140% AMI, curso HUD; si vendes antes del año 7, devuelves parte de la ganancia |
| Ingreso para una cuota de $2,200 | **~$52,800/año** en el borde (50%, sin otras deudas); ~$85,000 holgado (31%) | `TECHO_BORDE` / `TECHO_HOLGADO` |
| 5 años de renta a $2,200 | **$132,000** | |

**Guion (9 escenas; voz de Nelson; números quemados en edición):**

1. **Gancho:** «Este es un mensaje para los que pagan más de dos mil dólares de renta.»
2. **Lo que crees:** «Tú crees que comprar es carísimo. Vamos a sacar la cuenta. Fácil.»
3. **Lo que compra tu renta:** «Si hoy pagas dos mil doscientos de renta… con ese mismo dinero, cada mes,
   podrías pagar un condo de doscientos treinta mil. Y eso ya incluye todo: el préstamo, los impuestos y
   el seguro.»
4. **La trampa del condominio:** «Pero ojo. Los condominios cobran una cuota todos los meses. Y cada cien
   dólares de cuota es como si el condo se te encogiera doce mil dólares. Con una cuota de trescientos, ya
   no te alcanza para uno de doscientos treinta mil. Te alcanza para uno de ciento noventa y seis.»
5. **Lo que te falta:** «Entonces, ¿qué te falta? La cuota, no: esa ya la pagas cada mes. Te falta la
   llave: el dinero para entrar. Para ese condo, son entre catorce y veinte mil. Es la entrada más lo que
   se paga el día que firmas.»
6. **La ayuda:** «Y aquí viene lo bueno. El condado de Miami-Dade te puede prestar hasta treinta y cinco
   mil para la entrada. Sin intereses. Y no pagas nada cada mes: lo devuelves cuando vendas. Tú pones de
   tu bolsillo al menos el uno por ciento: en ese condo, unos dos mil trescientos. No lo cubre todo, pero
   cambia la cuenta.»
7. **¿Y el banco?:** «¿Y el banco te lo aprueba? Regla fácil: la casa se puede llevar, como mucho, la
   mitad de lo que ganas antes de impuestos. Para una cuota de dos mil doscientos, tienes que ganar unos
   cincuenta y tres mil al año, si no debes nada más.»
8. **El giro:** «Míralo así: tú ya pagas una hipoteca. La de tu landlord. En cinco años le vas a dar
   ciento treinta y dos mil dólares… y la casa sigue siendo de él.»
9. **Cierre:** «Esa fue la cuenta de alguien como tú. La tuya, con tu crédito y lo que tienes ahorrado,
   te la hago yo. Y si te falta algo, te ayudamos a estar listo. Comenta CASA. Soy Nelson, realtor. Ese
   era tu mensaje.»

**Letra chica fija:** ejemplo con FHA 3.5%, tasa FHA del día (FRED), impuesto 2%, seguro promedio del
condado; con FHA el edificio debe estar aprobado por HUD; requisitos de la ayuda de Miami-Dade; orienta,
no es una aprobación; firma con licencia (FL SL3654769). Nada segmenta por origen, sexo, edad o familia.

**Pendientes del guion:** confirmar en el MLS que hay condos de ~$230K aprobados por FHA (si no, subir el
gancho a $2,500 de renta). «Comenta CASA» necesita el mensaje automático por privado (no está montado;
mientras tanto, botón del anuncio).

---

## 5 · El formato: cocina, a lo Splitero

**Referencia:** anuncio de **Splitero** (préstamos sobre el equity de la casa) en Facebook. En la
biblioteca de anuncios de Meta hay 8 anuncios suyos «Explore Your Options» lanzados el **22-sep-2026**
(p. ej. `https://www.facebook.com/ads/library/?id=1728458918239265`, page_id `110655001514167`). Es una
prueba de ellos, **no un éxito demostrado**; única señal: 31 guardados contra 3 likes. No está en su
YouTube. Nelson lo guardó después del 14-sep (no está en `studio/scouting/guardados-*`).

**Qué hace (visto en 6 capturas que mandó Nelson):**

| Capa | Qué se ve |
|---|---|
| La tarea | Un señor hace el desayuno completo (aguacate, taza, café, huevos) y **termina sirviendo el plato y llevándolo a la mesa**. El desayuno es el reloj del video y su final es el final del mensaje |
| Título fijo arriba | Recuadro blanco: «The HELOC experience / There's a better way» |
| Subtítulos palabra por palabra | Letra condensada gruesa, palabra clave en rojo, borde negro |
| La lista que crece | Tarjetas blancas que se apilan: «Unknown Caller», «Application submitted, 30-60 days», «Income verification required», «Your new rate: 7.8% APR» |
| Insertos | Pantalla de llamada entrante («No Caller ID») sobre la cocina; fondo de papeles |
| Primera persona | «Me three weeks…» |
| Look | Cocina real y vieja, luz plana, cámara fija de celular, mira más la tarea que la cámara |

**Nuestra versión:** la IA hace la base (Nelson cocinando, siempre la misma cocina y la misma ropa) y en
edición van el título fijo, los subtítulos, **las tarjetas con los números que se apilan** (la cuenta
completa al final) y uno o dos insertos (p. ej. «Renta vence mañana: $2,200» sobre la cocina).

**El desayuno repartido en el guion (propuesta, no cerrada):**

| Paso | Escenas |
|---|---|
| 1. Pasa el aguacate al bowl (**clip hecho**) | 1–2 gancho |
| 2. Monta la cafetera (cafecito) | 3 lo que compra tu renta |
| 3. Rompe los huevos (**bloque hecho**) | 4 la trampa de la cuota |
| 4. Tuesta el pan | 5–6 lo que falta + la ayuda |
| 5. Sirve el plato y el café | 7 el banco |
| 6. Lleva todo a la mesa y se sienta | 8–9 el giro y el cierre |

Casi siempre mira la tarea: su voz puede ir corrida y la boca solo tiene que sincronizar cuando levanta la
vista. Lo difícil para la IA: romper huevos y servir café (manos precisas); se corta antes de ese momento
si falla. Estimado de la pieza completa: ~12 clips de 5 s, ~180 créditos a 480p.

**Evidencia de que el mecanismo está probado** (no del anuncio de Splitero en sí): Mady Mills (bolsa
mientras se arregla), Nara Smith (cocina con narración plana), Humphrey Yang (objetos que hacen visible el
número); un estudio de 2026 (Cognitive Research, split-screen) no encontró que el video secundario
empeore la comprensión.

---

## 6 · Assets e IDs (Higgsfield, cuenta de Nelson)

| Qué | ID | Nota |
|---|---|---|
| Avatar de Nelson (Element) | `9f7b6d3f-bc9b-47e2-8c26-989e7c425614` (`nelson-v5-dressed`) | camisa de lino azul claro, calvo, afeitado |
| Grabado náutico (prop) | `f49a37b2-17fa-4067-88a5-3cd43a7e5273` (`mensaje-mapa`) | usado solo en el storyboard A |
| Voz clonada | `7a25da09-a26c-4948-a991-fa81a203ead7` (`nelson-voz-v3`), v2 `58c878e1-17ce-4183-a60b-a59931f686d3` | con `seed_audio` **falló** (job `eab3f5e8`); con `text2speech_v2` variant `elevenlabs` funcionó |
| **Su voz real** (referencia de tono) | media `2b58b5ab-5d22-4493-82cf-58dd05421413` | nota de WhatsApp de El Claxon, toma 2 del 24-sep, 16.8 s, elegida por Nelson |
| Storyboard A (natural) / B (estudio) | `a19cc1c5-3495-4229-8a24-ceeaab477f29` / `64c9b87f-a885-4693-a2f4-1bb608ba3d5f` | **rechazados** |
| Cocina, foto opción 1 / **opción 2 (elegida)** | `2624682c-4bbc-4857-9c10-5dc19b69d1a8` / `53e47835-6515-4c99-b3a9-577dc322b22b` | la 2 traía un teléfono en la esquina |
| **Cocina sin el teléfono (base de continuidad)** | `0d5bb9db-e7d2-499c-a20f-33a6e44b55b9` | usar como `image_references` para toda la cocina |
| Audio del gancho (clon, ElevenLabs) | `719ef3fc-8c21-465b-bf96-85811f9e0ff7` | |
| **Clip 1 · gancho con aguacate (5 s)** | `0c90dc1d-511e-4ea9-a6ba-778abce5ce2b` | aprobado: «Video bien» |
| Foto de arranque · estufa con huevos | `db219468-87d8-46e3-80ba-25626eb963c0` | hecha desde `0d5bb9db` |
| **Bloque huevos (17 s)** | `b1c56b0f-91bb-4ba5-8b7d-884edf260071` | voz del modelo con `2b58b5ab` como `audio_references`; **sin revisar** |

URLs de resultado: `https://d8j0ntlcm91z4.cloudfront.net/user_36cfr0plJt7eQqcK83OjeHA0YJ9/hf_20260926_…`
(el CDN está bloqueado en la nube: desde esta sesión no se pudieron ver ni revisar a fotograma).

**Receta que funcionó** (coherente con `studio/pieces/el-claxon/PROMPTS.md`):

- Foto de arranque con `nano_banana_pro` (2 créditos a 2K; Higgsfield la corrió como Nano Banana 2),
  **la cocina anterior como `image_references`** y sin volver a citar el Element de Nelson (dos caras
  distintas se promedian).
- Pedir look de **video de celular**, no de foto: «everything in focus like a phone camera, plain mixed
  daylight, slight phone-camera noise, no cinematic lighting, no shallow depth of field, no color grading».
- Video con `seedance_2_5`, `mode: omni_reference`, `start_image` + `audio_references`, `generate_audio:
  true`, 480p, 9:16 (3 créditos por segundo). Rechazar el falso positivo de preset con
  `declined_preset_id: 24bae836-2c4a-48e0-89b6-49fcc0b21612` («IN THE DARK»).
- `audio_references` es **referencia de timbre, no pista maestra**: el modelo rehace la voz. Números
  escritos en palabras. Prompt en inglés con tramos por segundo, diálogo en español entre comillas.

**Prompt del bloque de huevos** (para repetir o corregir):

```
A real vertical phone video. The phone sits still on the kitchen counter the whole time. Same man and same
kitchen as the start image. He is cooking breakfast and talking to the viewer at the same time, mostly
looking at the pan and looking up at the camera for the numbers.
0 to 5 s: He cracks the egg on the rim of the black frying pan and lets it drop in; it starts to sizzle.
Looking at the pan, he says in Spanish: "Pero ojo. Los condominios cobran una cuota todos los meses."
5 to 10 s: He takes a second egg from the carton, looks up at the camera and says: "Y cada cien dólares de
cuota es como si el condo se te encogiera doce mil dólares." He cracks the second egg into the pan.
10 to 17 s: He moves the eggs with the spatula, glances at the camera and says: "Con una cuota de
trescientos, ya no te alcanza para uno de doscientos treinta mil. Te alcanza para uno de ciento noventa y
seis." Then he looks back down at the pan and keeps cooking.
He keeps his hands busy with the cooking the whole time he talks. His voice is the voice of the audio
reference: his own clear, bright, medium-high male voice, relaxed and conversational, calm and
matter-of-fact, like explaining something to a friend while he cooks, at a natural pace with short pauses
between sentences.
Sound: the sizzle of the eggs in the pan, the spatula on the pan, a quiet kitchen behind his voice. No music.
```

---

## 7 · Lo que falta decidir o hacer (en orden)

1. **Revisión de Nelson del bloque de huevos** (`b1c56b0f`), en 4 puntos: (a) ¿los huevos se rompen y
   caen bien o las manos se ven raras?; (b) ¿la voz suena a él, con el tono de El Claxon?; (c) ¿dice bien
   «doce mil», «doscientos treinta mil», «ciento noventa y seis»?; (d) ¿sigue cocinando mientras habla o
   se congela? Si falla una sola, se corrige esa y se vuelve a tirar.
2. **Decidir la voz de la serie:** voz del modelo con su audio real de referencia (lo del bloque de
   huevos) o su voz grabada entera. Si falla la voz, Nelson graba una nota y se regenera.
3. **Cerrar el mapa del desayuno** (§ 5) y generar las fotos de arranque de los pasos que faltan desde
   `0d5bb9db` (~2 créditos cada una), luego los clips.
4. **La plantilla de edición:** título fijo, subtítulos con palabra clave en rojo terracota de Umbralio
   (`#B34A28`), tarjetas que se apilan con los números, un inserto. Tipografías de la marca: Outfit y DM
   Mono.
5. **Medir contra EL MENSAJE:** mismo guion en los dos formatos; gana el que traiga más gente al
   cuestionario con perfil amarillo o verde, no el de más vistas.
6. **Montar el «comenta CASA → mensaje privado → guía»** (no existe todavía).
7. Confirmar en el MLS los condos de ~$230K aprobados por FHA.
8. Después: lista de ~50 episodios con lo ya verificado (motor + 16 guías + programas); 180 con research
   semanal. Temas propuestos: renta, crédito, dinero para entrar, lo que ganan, cómo ganan, mitos, el
   proceso, «Miami de verdad» (condos, inundación, seguro, homestead).

---

## 8 · Frente B — Proyecto de influencer IA (aparte, en pausa)

- **Origen:** video de Mark Tilbury «I Tried The LAZIEST Way to Make Money With AI» (3.2M vistas,
  patrocinado por Higgsfield, código TILBURY). 3 personajes (salud, dinero, relaciones), solo Instagram,
  cuaderno de $12: 23 ventas, **$157 de ganancia**; perdió su reto de $1,000. Quien ganó fue Mark (vistas
  + patrocinio).
- **Hallazgos 2026:** los «expertos» de IA en salud/finanzas son zona roja (YouTube, TikTok); el pago
  por vistas para IA pura se está cerrando (TikTok marcó «no original» a Granny Spills; Shorts pide 10M
  vistas/90 días desde feb-2027; Snapchat dejó de recomendar video 100% IA); Facebook Creator Fast Track
  paga $1,000/mes × 3 con 100K seguidores en otra red; las marcas se enfrían con la IA (86% → 60%).
- **Plan propuesto:** personaje cómico abiertamente IA (no experto), en TikTok + Instagram + Facebook;
  primer dinero: videos personalizados del personaje (Granny Spills vende en Cameo); segundo: contar el
  proceso con afiliado de Higgsfield (hasta 25% por 12 meses). Tres personajes a probar: Earl (91, intenta
  cada tendencia), Brenda (presidenta de la HOA), Palm Court (mini-serie en un condominio de retirados en
  Florida). Decidir en el día 21 por compartidos cada 1,000 vistas. Pendiente: que Nelson elija, horas por
  semana y si narraría el proceso con su voz.

---

## 9 · Fuentes principales

- YouTube, personajes de IA como expertos: https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/
- YouTube, cambios 2027: https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/
- TikTok, cuentas de IA en temas sensibles: https://www.searchenginejournal.com/tiktok-targets-ai-generated-spam-accounts-in-high-risk-topics/582256/
- Instagram, perfiles de IA: https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/
- Facebook Creator Fast Track: https://about.fb.com/news/2026/03/creator-fast-track-grow-your-audience-earn-money-on-facebook/
- Granny Spills: https://time.com/7329699/ai-influencers-tiktok-granny-spills/
- Nara Smith: https://www.harpersbazaararabia.com/culture/junior/the-un-trad-rise-of-nara-aziza-smith
- Humphrey Yang: https://fortune.com/2020/03/21/tik-tok-influencers-personal-finance-advice/
- Split-screen y comprensión (2026): https://link.springer.com/article/10.1186/s41235-026-00720-2
- Higgsfield Earn / afiliados: https://higgsfield.ai/earn · https://higgsfield.ai/blog/higgsfield-affiliate-program-2026
