PAV - P3: estimación de pitch
=============================

Esta práctica se distribuye a través del repositorio GitHub [Práctica 3](https://github.com/albino-pav/P3).
Siga las instrucciones de la [Práctica 2](https://github.com/albino-pav/P2) para realizar un `fork` de la
misma y distribuir copias locales (*clones*) del mismo a los distintos integrantes del grupo de prácticas.

Recuerde realizar el *pull request* al repositorio original una vez completada la práctica.

Ejercicios básicos
------------------

- Complete el código de los ficheros necesarios para realizar la estimación de pitch usando el programa
  `get_pitch`.

   * Complete el cálculo de la autocorrelación e inserte a continuación el código correspondiente.

   >Para estimar la frecuencia fundamental ($f_0$) en el dominio temporal empleamos la **autocorrelación sesgada** de la trama enventanada $x[n]$ de longitud $N$ muestras (`x.size()`). Para cada desplazamiento o retardo (*lag*) $l \in [0, \text{npitch\_max}-1]$, se inicializa `r[l]` a cero, se acumula el producto $x[n] \cdot x[n+l]$ para $0 \le n < N - l$ y se divide por $N$. De este modo, $r[0]$ representa directamente la potencia media de la trama y el estimador presenta menor varianza para retardos elevados. Adicionalmente, se ha implementado la ventana de Hamming en el método `set_window()`.

   ```cpp
   void PitchAnalyzer::autocorrelation(const vector<float> &x, vector<float> &r) const {

     for (unsigned int l = 0; l < r.size(); ++l) {
       /// \TODO Compute the autocorrelation r[l]
       /// \DONE Cálculo de la autocorrelación sesgada r[l] para cada retardo (lag) l:
       r[l] = 0.0F; // Inicializamos la autocorrelación en el lag l a cero
       for (unsigned int n = 0; n < x.size() - l; ++n) {
         r[l] += x[n] * x[n + l]; // Acumulamos el producto de la señal desplazada l muestras
       }
       r[l] /= x.size(); // Normalizamos por el número total de muestras N de la trama
     }

     if (r[0] == 0.0F) // to avoid log() and divide zero 
       r[0] = 1e-10; 
   }
   ```

   * Inserte una gŕafica donde, en un *subplot*, se vea con claridad la señal temporal de un segmento de
     unos 30 ms de un fonema sonoro y su periodo de pitch; y, en otro *subplot*, se vea con claridad la
	 autocorrelación de la señal y la posición del primer máximo secundario.

	 NOTA: es más que probable que tenga que usar Python, Octave/MATLAB u otro programa semejante para
	 hacerlo. Se valorará la utilización de la biblioteca matplotlib de Python.

   >Mediante el script `scripts/plot_autocorr.py` (utilizando `numpy` y `matplotlib` en Python), se ha extraído una trama sonora de $30\text{ ms}$ ($N = 600$ muestras a $f_s = 20\text{ kHz}$) perteneciente al archivo `pitch_db/train/sb002.wav` en el instante $t = 0.66\text{ s}$.

   >En el primer *subplot* se observa la clara estructura casi periódica del fonema sonoro en el dominio temporal, señalando su periodo fundamental $T_0 = 4.05\text{ ms}$. En el segundo *subplot* se representa la función de autocorrelación sesgada $r[l]$, donde se distingue el máximo principal en el origen ($l = 0$, igual a la potencia media de la trama) y se localiza el **primer máximo secundario** fuera del lóbulo central en el retardo $l = 81\text{ muestras}$ (dentro del rango de búsqueda $l \in [40, 400]$ muestras correspondiente a $[50, 500]\text{ Hz}$). Esto determina directamente un periodo de pitch $T_0 = 81 / 20000 = 4.05\text{ ms}$ y una frecuencia fundamental estimada de $f_0 = 20000 / 81 \approx 246.9\text{ Hz}$.

   ![Señal temporal y autocorrelación de un segmento sonoro](img/autocorrelacion_pitch.png)

   * Determine el mejor candidato para el periodo de pitch localizando el primer máximo secundario de la
     autocorrelación. Inserte a continuación el código correspondiente.

   * Implemente la regla de decisión sonoro o sordo e inserte el código correspondiente.

   * Puede serle útil seguir las instrucciones contenidas en el documento adjunto `código.pdf`.

- Una vez completados los puntos anteriores, dispondrá de una primera versión del estimador de pitch. El 
  resto del trabajo consiste, básicamente, en obtener las mejores prestaciones posibles con él.

  * Utilice el programa `wavesurfer` para analizar las condiciones apropiadas para determinar si un
    segmento es sonoro o sordo. 
	
	  - Inserte una gráfica con la estimación de pitch incorporada a `wavesurfer` y, junto a ella, los 
	    principales candidatos para determinar la sonoridad de la voz: el nivel de potencia de la señal
		(r[0]), la autocorrelación normalizada de uno (r1norm = r[1] / r[0]) y el valor de la
		autocorrelación en su máximo secundario (rmaxnorm = r[lag] / r[0]).

		Puede considerar, también, la conveniencia de usar la tasa de cruces por cero.

	    Recuerde configurar los paneles de datos para que el desplazamiento de ventana sea el adecuado, que
		en esta práctica es de 15 ms.

      - Use el estimador de pitch implementado en el programa `wavesurfer` en una señal de prueba y compare
	    su resultado con el obtenido por la mejor versión de su propio sistema. Inserte una gráfica
		ilustrativa del resultado de ambos estimadores.

        Tenga en cuenta que `wavesurfer` usa un desplazamiento de ventana que no tiene por qué coincidir
        con el de su programa. Ajústelo convenientemente para realizar la comparación.
     
		Aunque puede usar el propio Wavesurfer para obtener la representación, se valorará
	 	el uso de alternativas de mayor calidad (particularmente Python).
  
  * Optimice los parámetros de su sistema de estimación de pitch e inserte una tabla con las tasas de error
    y el *score* TOTAL proporcionados por `pitch_evaluate` en la evaluación de la base de datos 
	`pitch_db/train`..

Ejercicios de ampliación
------------------------

- Usando la librería `docopt_cpp`, modifique el fichero `get_pitch.cpp` para incorporar los parámetros del
  estimador a los argumentos de la línea de comandos.
  
  Esta técnica le resultará especialmente útil para optimizar los parámetros del estimador. Recuerde que
  una parte importante de la evaluación recaerá en el resultado obtenido en la estimación de pitch en la
  base de datos.

  * Inserte un *pantallazo* en el que se vea el mensaje de ayuda del programa y un ejemplo de utilización
    con los argumentos añadidos.

- Implemente las técnicas que considere oportunas para optimizar las prestaciones del sistema de estimación
  de pitch.

  Entre las posibles mejoras, puede escoger una o más de las siguientes:

  * Técnicas de preprocesado: filtrado paso bajo, diezmado, *center clipping*, etc.
  * Técnicas de postprocesado: filtro de mediana, *dynamic time warping*, etc.
  * Métodos alternativos a la autocorrelación: procesado cepstral, *average magnitude difference function*
    (AMDF), etc.
  * Optimización **demostrable** de los parámetros que gobiernan el estimador, en concreto, de los que
    gobiernan la decisión sonoro/sordo.
  * Cualquier otra técnica que se le pueda ocurrir o encuentre en la literatura.

  Encontrará más información acerca de estas técnicas en las [Transparencias del Curso](https://atenea.upc.edu/pluginfile.php/2908770/mod_resource/content/3/2b_PS%20Techniques.pdf)
  y en [Spoken Language Processing](https://discovery.upc.edu/iii/encore/record/C__Rb1233593?lang=cat).
  También encontrará más información en los anexos del enunciado de esta práctica.

  Incluya, a continuación, una explicación de las técnicas incorporadas al estimador. Se valorará la
  inclusión de gráficas, tablas, código o cualquier otra cosa que ayude a comprender el trabajo realizado.

  También se valorará la realización de un estudio de los parámetros involucrados. Por ejemplo, si se opta
  por implementar el filtro de mediana, se valorará el análisis de los resultados obtenidos en función de
  la longitud del filtro.
   

Evaluación *ciega* del estimador
-------------------------------

Antes de realizar el *pull request* debe asegurarse de que su repositorio contiene los ficheros necesarios
para compilar los programas correctamente ejecutando `make release`.

Con los ejecutables construidos de esta manera, los profesores de la asignatura procederán a evaluar el
estimador con la parte de test de la base de datos (desconocida para los alumnos). Una parte importante de
la nota de la práctica recaerá en el resultado de esta evaluación.
