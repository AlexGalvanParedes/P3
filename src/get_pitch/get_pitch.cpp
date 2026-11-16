/// @file

#include <iostream>
#include <fstream>
#include <string.h>
#include <errno.h>
#include <algorithm>
#include <cmath>

#include "wavfile_mono.h"
#include "pitch_analyzer.h"

#include "docopt.h"

#define FRAME_LEN   0.030 /* 30 ms. */
#define FRAME_SHIFT 0.015 /* 15 ms. */

using namespace std;
using namespace upc;

static const char USAGE[] = R"(
get_pitch - Pitch Estimator 

Usage:
    get_pitch [options] <input-wav> <output-txt>
    get_pitch (-h | --help)
    get_pitch --version

Options:
    -h, --help  Show this screen
    --version   Show the version of the project
    --window=<win>            Window type (HAMMING or RECT) [default: HAMMING]
    --f0-min=<fmin>           Minimum pitch frequency in Hz [default: 55.0]
    --f0-max=<fmax>           Maximum pitch frequency in Hz [default: 400.0]
    --pot-th=<pth>            Power threshold in dB for voiced/unvoiced [default: -47.0]
    --r1-th=<r1th>            Normalized lag-1 autocorrelation threshold [default: 0.82]
    --rmax-th=<rmaxth>        Normalized secondary peak threshold [default: 0.33]
    --clip-th=<cth>           Center clipping threshold ratio (0.0 disables it) [default: 0.0]
    --median-len=<mlen>       Median filter length in frames (odd integer, 1 disables it) [default: 5]

Arguments:
    input-wav   Wave file with the audio signal
    output-txt  Output file: ASCII file with the result of the estimation:
                    - One line per frame with the estimated f0
                    - If considered unvoiced, f0 must be set to f0 = 0
)";

int main(int argc, const char *argv[]) {
	/// \TODO 
	///  Modify the program syntax and the call to **docopt()** in order to
	///  add options and arguments to the program.
  /// \DONE Se han añadido a USAGE y procesado mediante docopt() las opciones para configurar
  /// el tipo de ventana (--window), el rango de frecuencias (--f0-min, --f0-max), los umbrales
  /// de sonoridad (--pot-th, --r1-th, --rmax-th), el preprocesado de center-clipping (--clip-th)
  /// y la longitud del filtro de mediana en postprocesado (--median-len).
    std::map<std::string, docopt::value> args = docopt::docopt(USAGE,
        {argv + 1, argv + argc},	// array of arguments, without the program name
        true,    // show help if requested
        "2.0");  // version string

	std::string input_wav = args["<input-wav>"].asString();
	std::string output_txt = args["<output-txt>"].asString();
  std::string win_str = args["--window"].asString();
  float f0_min = std::stof(args["--f0-min"].asString());
  float f0_max = std::stof(args["--f0-max"].asString());
  float pot_th = std::stof(args["--pot-th"].asString());
  float r1_th = std::stof(args["--r1-th"].asString());
  float rmax_th = std::stof(args["--rmax-th"].asString());
  float clip_th = std::stof(args["--clip-th"].asString());
  int median_len = std::stoi(args["--median-len"].asString());

  // Read input sound file
  unsigned int rate;
  vector<float> x;
  if (readwav_mono(input_wav, rate, x) != 0) {
    cerr << "Error reading input file " << input_wav << " (" << strerror(errno) << ")\n";
    return -2;
  }

  int n_len = rate * FRAME_LEN;
  int n_shift = rate * FRAME_SHIFT;

  // Select window type
  PitchAnalyzer::Window win_type = (win_str == "RECT") ? PitchAnalyzer::RECT : PitchAnalyzer::HAMMING;

  // Define analyzer
  PitchAnalyzer analyzer(n_len, rate, win_type, f0_min, f0_max, pot_th, r1_th, rmax_th);

  /// \TODO
  /// Preprocess the input signal in order to ease pitch estimation. For instance,
  /// central-clipping or low pass filtering may be used.
  /// \DONE Implementación de Center Clipping con offset sobre la señal de entrada x[n]:
  /// Si clip_th > 0, se calcula el umbral absoluto X_th = clip_th * max(|x[n]|) y se anulan
  /// las muestras de amplitud inferior a X_th desplazando el resto para mantener continuidad.
  if (clip_th > 0.0F && !x.empty()) {
    float max_abs = 0.0F;
    for (unsigned int i = 0; i < x.size(); ++i) {
      if (std::fabs(x[i]) > max_abs)
        max_abs = std::fabs(x[i]); // Buscamos la amplitud máxima de la señal
    }
    float x_th = clip_th * max_abs; // Umbral de clipping proporcional al máximo
    for (unsigned int i = 0; i < x.size(); ++i) {
      if (x[i] > x_th)
        x[i] = x[i] - x_th;         // Desplazamiento positivo (con offset)
      else if (x[i] < -x_th)
        x[i] = x[i] + x_th;         // Desplazamiento negativo (con offset)
      else
        x[i] = 0.0F;                // Anulación central para |x[n]| <= x_th
    }
  }

  // Iterate for each frame and save values in f0 vector
  vector<float>::iterator iX;
  vector<float> f0;
  for (iX = x.begin(); iX + n_len < x.end(); iX = iX + n_shift) {
    float f = analyzer(iX, iX + n_len);
    f0.push_back(f);
  }

  /// \TODO
  /// Postprocess the estimation in order to supress errors. For instance, a median filter
  /// or time-warping may be used.
  /// \DONE Implementación de un filtro de mediana de longitud impar (median_len) sobre el contorno f0:
  /// Para cada trama i, se toma una ventana centrada de tamaño median_len, se ordenan sus valores
  /// con std::sort() y se selecciona el valor central (mediana), suprimiendo errores groseros
  /// (saltos a múltiplos/submúltiplos de pitch) y decisiones sonoro/sordo aisladas sin difuminar bordes.
  if (median_len > 1 && f0.size() >= (unsigned int)median_len) {
    vector<float> f0_orig = f0; // Copia del contorno original antes del filtrado
    int half = median_len / 2;
    for (int i = 0; i < (int)f0.size(); ++i) {
      vector<float> win;
      for (int k = -half; k <= half; ++k) {
        int idx = i + k;
        if (idx < 0) idx = 0;
        if (idx >= (int)f0_orig.size()) idx = (int)f0_orig.size() - 1;
        win.push_back(f0_orig[idx]); // Extraemos las muestras vecinas de la ventana
      }
      std::sort(win.begin(), win.end()); // Ordenamos los valores de la ventana
      f0[i] = win[half];                 // Asignamos el elemento mediano
    }
  }

  // Write f0 contour into the output file
  ofstream os(output_txt);
  if (!os.good()) {
    cerr << "Error reading output file " << output_txt << " (" << strerror(errno) << ")\n";
    return -3;
  }

  os << 0 << '\n'; //pitch at t=0
  for (iX = f0.begin(); iX != f0.end(); ++iX) 
    os << *iX << '\n';
  os << 0 << '\n';//pitch at t=Dur

  return 0;
}
