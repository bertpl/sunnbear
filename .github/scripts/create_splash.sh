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
DISPLAY_VERSION="$1"  # WITHOUT leading "v" (the annotation adds it), e.g. "0.1.10" or "0.1.11-dev"

# --- create splash without version info ---
if [ ! -f ./images/_splash_without_version.webp ]; then
    magick -pointsize 100 -background transparent \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#efefef" label:"S" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#9a9a9a" label:"........ " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#efefef" label:"UN" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#9a9a9a" label:"...... ." \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#efefef" label:"N" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#9a9a9a" label:"........ ......... ... " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#efefef" label:"B" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#9a9a9a" label:".... " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#efefef" label:"E" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#9a9a9a" label:"......... .. " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#efefef" label:"A" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#9a9a9a" label:"......... ... " \
           -font "./images/splash/google_fonts_montserrat_bold.ttf" -fill "#efefef" label:"R" \
           -font "./images/splash/google_fonts_montserrat_regular.ttf" -fill "#9a9a9a" label:"...-......." \
           +append "./images/header.mpc"
    magick "./images/splash/splash.webp" "./images/header.mpc" -gravity North -geometry +0+28 -composite \
           -quality 95 -define webp:lossless=false "./images/_splash_without_version.webp"
    rm ./images/header.mpc ./images/header.cache
fi

# --- add version info ---
# The background image (images/splash/splash.webp) shows "SUNNBEAR" written in chalk; the version sits just below that word, right-aligned with the end of the final "R".
# The splash is saved at half the background image's width, because the README displays it narrower than that half width.
magick "./images/_splash_without_version.webp" -pointsize 128 -font "./images/splash/google_fonts_montserrat_bold.ttf" -gravity East \
       -fill "black" -annotate +1077+163 "v${DISPLAY_VERSION}" \
       -fill "white" -annotate +1080+160 "v${DISPLAY_VERSION}" \
       -resize 50% -quality 90 -define webp:lossless=false "./images/splash_with_version.webp"
