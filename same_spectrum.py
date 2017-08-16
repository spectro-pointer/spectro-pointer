import glob
import struct
import compare_spectrum

def load_spectrum(filename):
    result = []

    with open(filename, "r") as file:
        for line in file:
            words = line.split()
            wavelength, spectrum = float(words[0]), int(float(words[1]))
            result.append(spectrum)

    return result

def load_spectrums(target_elevation, target_azimuth):
    DELTA_ELEVATION = 0.02
    DELTA_AZIMUTH = 20
    POSITION_FILENAME = "busca_positions.txt"
    SPECTRUM_FILENAME = "spectrum.txt"

    result = []

    for filename in glob.glob("captures/*/%s" % POSITION_FILENAME):
        with open(filename, "r") as file:
            words = file.read().split()
            elevation, azimuth = float(words[1]), int(words[3])
            if (abs(target_elevation - elevation) <= DELTA_ELEVATION and
                  abs(target_azimuth - azimuth) <= DELTA_AZIMUTH):

                spectrum_filename = "%s%s" % (filename[:-len(POSITION_FILENAME)], SPECTRUM_FILENAME)
                print spectrum_filename

                result.append((spectrum_filename, load_spectrum(spectrum_filename)))

    return result

if __name__ == "__main__":
    spectrums = load_spectrums(0.691783, 5325)
    for i in range(1, len(spectrums)):
        print "Spectrum %s vs %s" % (spectrums[0][0], spectrums[i][0])
        print "  %f" % compare_spectrum.cmp(spectrums[0][1], spectrums[i][1])
