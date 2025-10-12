#! /bin/sh
# ---------------------------------------------
# Input:  ./images/splash/*
# Output: ./images/splash_with_version.webp
# ---------------------------------------------

# --- check imagemagick version ---
echo "------ ImageMagick version info --------------------------------------------"
magick identify -version
echo "----------------------------------------------------------------------------"

# --- argument handling ---
DISPLAY_VERSION="$1"  # e.g. "v0.1.10" or "v0.1.11-dev"

# --- create splash without version info ---
if [ ! -f ./images/splash/_splash_without_version.png ]; then
    magick -pointsize 100 -background transparent \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#666666" label:"S" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#bbbbbb" label:"........ " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#666666" label:"UN" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#bbbbbb" label:"...... ." \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#666666" label:"N" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#bbbbbb" label:"........ ......... ... " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#666666" label:"B" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#bbbbbb" label:".... " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#666666" label:"E" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#bbbbbb" label:"......... .. " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#666666" label:"A" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#bbbbbb" label:"......... ... " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#666666" label:"R" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#bbbbbb" label:"...-......." \
           +append "./images/header.mpc"
    magick "./images/splash/splash.webp" "./images/header.mpc" -gravity North -geometry +0+5 -composite "./images/temp.mpc"
    magick -pointsize 36 -font "./images/splash/google_fonts_montserrat_italic.ttf" "./images/temp.mpc" -gravity SouthWest -fill "#ffffff" -annotate +10+5 "DiffusionBee 2.5.3 (FLUX.1-dev + Real-ESRGAN)" "./images/_splash_without_version.png"
fi

# --- add version info ---
magick -pointsize 128 -font "./images/splash/google_fonts_montserrat_bold.ttf" "./images/_splash_without_version.png" -gravity East -fill "black" -annotate +1262+273 "v${DISPLAY_VERSION}" "./images/temp.mpc"
magick -pointsize 128 -font "./images/splash/google_fonts_montserrat_bold.ttf" "./images/temp.mpc" -gravity East -fill "white" -annotate +1265+270 "v${DISPLAY_VERSION}" -quality 90 -define webp:lossless=false "./images/splash_with_version.webp"

# --- clean up ---
echo "Cleaning up..."
rm ./images/*.mpc
rm ./images/*.cache