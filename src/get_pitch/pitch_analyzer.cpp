/// @file

#include <iostream>
#include <math.h>
#include "pitch_analyzer.h"

using namespace std;

/// Name space of UPC
namespace upc {
  void PitchAnalyzer::autocorrelation(const vector<float> &x, vector<float> &r) const {

    for (unsigned int l = 0; l < r.size(); ++l) {
  		/// \TODO Compute the autocorrelation r[l]
      /// \DONE Cálculo de la autocorrelación sesgada r[l] para cada retardo (lag) l:
      /// - Inicializamos el acumulador r[l] a 0.
      /// - Acumulamos el producto cruzado x[n] * x[n + l] dentro de los límites de la trama.
      /// - Dividimos entre el tamaño total de la trama N = x.size() para normalizar (estimador sesgado).
      /// \f[
      ///   r[l] = \frac{1}{N}\sum_{n=0}^{N-1-l}x[n]x[n+l]
      /// \f]
      r[l] = 0.0F; // Inicializamos la autocorrelación en el lag l a cero
      for (unsigned int n = 0; n < x.size() - l; ++n) {
        r[l] += x[n] * x[n + l]; // Acumulamos el producto de la señal con su versión desplazada l muestras
      }
      r[l] /= x.size(); // Dividimos por el número total de muestras N de la trama (autocorrelación sesgada)
    }

    if (r[0] == 0.0F) //to avoid log() and divide zero 
      r[0] = 1e-10; 
  }

  void PitchAnalyzer::set_window(Window win_type) {
    if (frameLen == 0)
      return;

    window.resize(frameLen);

    switch (win_type) {
    case HAMMING:
      /// \TODO Implement the Hamming window
      /// \DONE Implementación de la ventana de Hamming estándar de longitud frameLen:
      /// w[i] = 0.54 - 0.46 * cos(2 * pi * i / (frameLen - 1))
      for (unsigned int i = 0; i < frameLen; ++i) {
        window[i] = 0.54F - 0.46F * cos((2.0F * M_PI * i) / (frameLen - 1)); // Coeficientes de Hamming
      }
      break;
    case RECT:
    default:
      window.assign(frameLen, 1);
    }
  }

  void PitchAnalyzer::set_f0_range(float min_F0, float max_F0) {
    npitch_min = (unsigned int) samplingFreq/max_F0;
    if (npitch_min < 2)
      npitch_min = 2;  // samplingFreq/2

    npitch_max = 1 + (unsigned int) samplingFreq/min_F0;

    //frameLen should include at least 2*T0
    if (npitch_max > frameLen/2)
      npitch_max = frameLen/2;
  }

  bool PitchAnalyzer::unvoiced(float pot, float r1norm, float rmaxnorm) const {
    /// \TODO Implement a rule to decide whether the sound is voiced or not.
    /// * You can use the standard features (pot, r1norm, rmaxnorm),
    ///   or compute and use other ones.
    /// \DONE Implementación y optimización de la regla de decisión sordo/sonoro parametrizada:
    /// Clasificamos la trama como sorda (true) empleando los umbrales configurables (pot_th, rmax_th, r1_th):
    /// 1) Si la potencia en dB es menor que pot_th (silencio o ruido de fondo).
    /// 2) Si el máximo secundario normalizado es menor que rmax_th (baja periodicidad).
    /// 3) Si la correlación a lag 1 (r1norm) es menor que r1_th (fricativa sorda), salvo que rmaxnorm > 0.50.
    if (pot < pot_th)
      return true;
    if (rmaxnorm < rmax_th)
      return true;
    if (r1norm < r1_th && rmaxnorm < 0.50F)
      return true;

    return false;
  }

  float PitchAnalyzer::compute_pitch(vector<float> & x) const {
    if (x.size() != frameLen)
      return -1.0F;

    //Window input frame
    for (unsigned int i=0; i<x.size(); ++i)
      x[i] *= window[i];

    vector<float> r(npitch_max);

    //Compute correlation
    autocorrelation(x, r);

    vector<float>::const_iterator iR = r.begin(), iRMax = iR;

    /// \TODO 
	/// Find the lag of the maximum value of the autocorrelation away from the origin.<br>
	/// Choices to set the minimum value of the lag are:
	///    - The first negative value of the autocorrelation.
	///    - The lag corresponding to the maximum value of the pitch.
    ///	   .
	/// In either case, the lag should not exceed that of the minimum value of the pitch.
  /// \DONE Búsqueda de la posición del máximo secundario de la autocorrelación usando iteradores
  /// y std::max_element() dentro del rango válido de retardos [npitch_min, npitch_max).
    iRMax = std::max_element(r.begin() + npitch_min, r.begin() + npitch_max); // Buscamos el máximo entre lag_min y lag_max
   
    unsigned int lag = iRMax - r.begin();

    float pot = 10 * log10(r[0]);

    //You can print these (and other) features, look at them using wavesurfer
    //Based on that, implement a rule for unvoiced
    //change to #if 1 and compile
#if 0
    if (r[0] > 0.0F)
      cout << pot << '\t' << r[1]/r[0] << '\t' << r[lag]/r[0] << endl;
#endif
    
    if (unvoiced(pot, r[1]/r[0], r[lag]/r[0]))
      return 0;
    else
      return (float) samplingFreq/(float) lag;
  }
}
