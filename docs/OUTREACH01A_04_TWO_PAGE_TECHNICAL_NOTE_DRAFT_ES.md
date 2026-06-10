# Un demostrador mínimo de identidad de estado para configuraciones equivalentes con desfase

*Una representación sintética y auditable preparada para evaluación técnica*

## 1. Propósito

Esta nota describe un demostrador sintético deliberadamente pequeño. Su propósito no es modelar un experimento láser descrito, reproducir una medición ni proponer una teoría nueva del comportamiento de cristales de tiempo discretos. Su propósito es más estrecho: hacer explícitas tres distinciones para que puedan evaluarse técnicamente. Las distinciones son identidad del registro, equivalencia dinámica y posición de fase temporal. Una cuarta cuestión, la representación de una frontera entre configuraciones equivalentes coexistentes, se incluye como pregunta abierta de modelización y no como ontología física propuesta.

El demostrador utiliza un único conjunto de datos canónico con tres registros: `DTC_A`, `DTC_B` y `BOUNDARY_AB`. Las capas de presentación en inglés y español pueden mostrar los mismos registros mediante alias localizados de campos y valores, pero no cambian el conjunto de datos, el esquema, el orden de los registros, los valores controlados, las reglas de validación ni la lógica de comparación.

Esto convierte la nota en una capa de presentación y no en un segundo conjunto de datos. Los mismos valores canónicos permanecen visibles entre acentos graves siempre que se muestra un alias localizado de valor.

## 2. Por qué esta representación

La forma elegida es intencionadamente mínima porque la pregunta técnica posterior no debería pedir a una persona lectora que evalúe un proyecto amplio. Debería preguntar si una representación compacta de identidad de estado es metodológicamente útil, trivial, engañosa o incompleta. Por eso la representación separa lo que se declara de manera sintética de lo que no queda establecido físicamente.

`DTC_A` y `DTC_B` se declaran como miembros de una misma clase de equivalencia dinámica. También se declaran como configuraciones que difieren por un período de excitación en el desfase temporal. Esto permite que la estructura de registros distinga una clase de equivalencia compartida de la identidad de un registro concreto. La distinción es importante para el demostrador porque dos registros pueden tratarse como dinámicamente equivalentes en un ejemplo metodológico sin ser el mismo registro y sin afirmar una identidad completa del estado físico.

El registro de frontera se incluye para concretar la segunda pregunta. No afirma que un objeto de frontera sea físicamente correcto. Solo proporciona un lugar visible donde una evaluación experta podría decir que un registro de frontera separado es útil, demasiado fuerte, demasiado débil o debería sustituirse por otra descripción dinámica.

## 3. Los tres registros

`DTC_A` es una configuración de estado sintética. Tiene la clase de estado `DTC_EQUIVALENT_PAIR`, la clase de equivalencia dinámica `DTC_EQ_CLASS_01`, el desfase temporal `0`, el desplazamiento en períodos de excitación `0` y el dominio `DOMAIN_A`. Su estado de identidad completa es `self_identical_only`, lo que significa que este registro solo es idéntico a sí mismo dentro del demostrador.

`DTC_B` es una segunda configuración de estado sintética. Tiene la misma clase de estado y la misma clase de equivalencia dinámica que `DTC_A`, pero el desfase temporal `1`, el desplazamiento en períodos de excitación `1` y el dominio `DOMAIN_B`. Su estado de identidad completa es `distinct_record_not_identical_to_DTC_A`. Así, el conjunto de datos marca explícitamente la equivalencia dinámica sin colapsar la identidad del registro.

`BOUNDARY_AB` es una configuración de frontera sintética. Su clase de estado es `DTC_BOUNDARY_CLASS`. No se asigna a `DTC_EQ_CLASS_01`; su clase de equivalencia dinámica, su desfase temporal y su desplazamiento en períodos de excitación son `not_applicable`. Su campo de dominio referencia `DOMAIN_A__DOMAIN_B`, y su función de frontera es `interface_between_equivalent_phase_shifted_domains`. Su estado de incertidumbre es `representation_choice_open`.

## 4. Identidad, equivalencia y desfase

El demostrador contiene tres reglas de protección. La similitud observable no implica identidad completa del estado. La equivalencia dinámica no implica identidad del registro. La equivalencia con desfase no implica pertenencia al mismo dominio. Estas afirmaciones no son resultados empíricos. Son reglas que impiden que el ejemplo pequeño introduzca una conclusión más fuerte de lo que puede sostener.

La clase de equivalencia dinámica se declara solo para la demostración metodológica. El conjunto de datos no infiere equivalencia a partir de datos experimentales. No estima parámetros, no reconstruye un mecanismo y no valida una interpretación física. Su valor es exponer la pregunta de contabilidad conceptual: si dos configuraciones se consideran equivalentes bajo un desplazamiento de un período, ¿qué información sigue siendo necesaria para decidir si son idénticas, meramente equivalentes o físicamente distinguibles?

## 5. La representación de la frontera como cuestión abierta

El registro de frontera separado es una opción de representación. Da a la frontera un identificador de registro, un tipo, una función y un estado de incertidumbre explícitos. Esto hace visible la frontera en la misma tabla que las configuraciones de estado, pero también crea un riesgo: la tabla podría parecer que valida el objeto de frontera como entidad física. Para evitarlo, el registro indica `representation_choice_open` y `not_experimental`.

El uso previsto es preguntar si esta representación es adecuada. Puede haber una respuesta mejor: una etiqueta de estado, una condición de interfaz, una región dinámica de transición, una variable de pared de dominio o una descripción específica de un modelo. El demostrador está diseñado para que esa crítica pueda formularse con facilidad.

## 6. Preguntas técnicas

1. ¿Es metodológicamente útil distinguir entre la identidad del registro, la equivalencia dinámica y la posición de fase temporal para dos configuraciones relacionadas por un desplazamiento de un período de excitación?

2. Desde la perspectiva del grupo, ¿cuál sería la representación mínima adecuada de fronteras de larga duración entre configuraciones equivalentes coexistentes: una etiqueta de estado, un objeto de frontera independiente u otra descripción dinámica?

3. ¿Cuál es la información mínima de estado u observable necesaria para que una comparación relacional de este tipo sea físicamente significativa y no solo formalmente coherente?

## 7. Alcance y limitaciones

Este es un demostrador metodológico sintético. No se utilizan datos experimentales. No es un modelo del experimento láser descrito. No hace ninguna predicción física y no explica ningún mecanismo. La equivalencia dinámica se declara, no se infiere. El registro de frontera separado es una opción abierta de representación, no una ontología validada. Los alias localizados en inglés o español son solo metadatos de presentación; no son claves, enlaces, entradas de validación ni entradas de lógica. No se renderiza ninguna figura en este bloque. No se redacta ni se envía ningún mensaje de contacto.
