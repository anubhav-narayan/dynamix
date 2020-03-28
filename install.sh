#!/usr/bin/env bash
# This script automatically detect the PulseEffects presets directory and installs the presets

check_installation() {
    if flatpak list | grep -q "com.github.wwmm.pulseeffects"; then
        PRESETS_DIRECTORY="$HOME/.var/app/com.github.wwmm.pulseeffects/config/PulseEffects"
        elif [ -d "$HOME/.config/PulseEffects" ]; then
        PRESETS_DIRECTORY="$HOME/.config/PulseEffects"
    else
        echo "Error! Couldn't find PulseEffects presets directory!"
        exit 1
    fi
}

check_impulse_response_directory() {
    if [ ! -d "$PRESETS_DIRECTORY/irs" ]; then
        mkdir "$PRESETS_DIRECTORY/irs"
    fi
}

install_presets(){
        echo "Installing DynaMIX Impulse Response..."
        # curl "https://raw.githubusercontent.com/anubhav-narayan/dynamix/master/DynaMIX(44.1kHz)2.irs" --output "$PRESETS_DIRECTORY/irs/DynaMIX(44.1kHz)2.irs" --silent
        curl "https://raw.githubusercontent.com/anubhav-narayan/dynamix/master/irs/DynaMIX(48kHz)2.irs" --output "$PRESETS_DIRECTORY/irs/DynaMIX(48kHz)2.irs" --silent
        curl "https://raw.githubusercontent.com/anubhav-narayan/dynamix/master/irs/DynaMIX(96kHz)2.irs" --output "$PRESETS_DIRECTORY/irs/DynaMIX(96kHz)2.irs" --silent
}

check_installation
check_impulse_response_directory
install_presets
echo "Done"