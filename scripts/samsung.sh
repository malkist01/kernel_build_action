#!/usr/bin/env bash

# Dependencies
rm -rf kernel
git clone $REPO -b $BRANCH kernel
cd kernel
    rm -rf gcc
    echo "Cloning gcc"
    
  git clone https://github.com/LineageOS/android_prebuilts_gcc_linux-x86_aarch64_aarch64-linux-gnu-9.3.git -b lineage-22.1 --depth=1 gcc
        
	PATH="${PWD}/gcc/bin:${PATH}"
	
    sudo apt install -y ccache
    echo "Done"
    
PROCS=$(nproc --all)
tanggal=$(TZ=Asia/Jakarta date +'%H%M-%d%m%y')
START=$(date +"%s")
IMAGE=$(pwd)/out/arch/arm64/boot/Image.gz-dtb
KERNEL_DIR=$(pwd)
ARCH=arm64
export ARCH
export CODENAME
DEFCONFIG="teletubies_defconfig"
export DEFCONFIG
export USE_CCACHE=1
export KBUILD_BUILD_USER=malkist
export KBUILD_BUILD_HOST=android
DEVICE="samsung"
export DEVICE
CODENAME="j6primelte"
export CODENAME
# sticker plox
function sticker() {
        curl -s -X POST "https://api.telegram.org/bot$token/sendSticker" \
                        -d sticker="CAACAgUAAxkBAAMPXvdff5azEK_7peNplS4ywWcagh4AAgwBAALQuClVMBjhY" \
                        -d chat_id=$chat_id
}
# Send info plox channel
function sendinfo() {
        curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
                        -d chat_id=$chat_id \
                        -d "disable_web_page_preview=true" \
                        -d "parse_mode=html" \
                        -d text="<b>Teletubies</b> CI Triggered%0ABuild started on <code>Drone CI/CD</code>%0AFor device <b>Samsung J6primelte</b>%0Abranch <code>$(git rev-parse --abbrev-ref HEAD)</code> (Android 10-11)%0AUnder commit <code>$(git log --pretty=format:'"%h : %s"' -1)</code>%0AUsing compiler: <code>$(${GCC}gcc --version | head -n 1 | perl -pe 's/\(http.*?\)//gs' | sed -e 's/  */ /g')</code>%0AStarted on <code>$(TZ=Asia/Jakarta date)</code>%0A<b>Build Status:</b> #Stable"
}
# Send private info
function sendpriv() {
        curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
                        -d chat_id=$priv_id \
                        -d "disable_web_page_preview=true" \
                        -d "parse_mode=html" \
                        -d text="Teletubies CI Started%0ADrone triggered by: <code>${DRONE_BUILD_EVENT}</code> event%0AJob name: <code>Baking</code>%0ACommit point: <a href='${DRONE_COMMIT_LINK}'>$(git log --pretty=format:'"%h : %s"' -1)</a>%0A<b>Pipeline jobs</b> <a href='https://cloud.drone.io/najahiiii/moaikernal/${DRONE_BUILD_NUMBER}'>here</a>"
}
# Push kernel to channel
function push() {
        cd AnyKernel
	ZIP=$(echo *.zip)
	curl -F document=@$ZIP "https://api.telegram.org/bot$token/sendDocument" \
			-F chat_id="$chat_id" \
			-F "disable_web_page_preview=true" \
			-F "parse_mode=html" \
			-F caption="Build took $(($DIFF / 60)) minute(s) and $(($DIFF % 60)) second(s). | For <b>Xiaomi Redmi 4A/5A (Rolex/Riva)</b> | <a href='${HASIL}'>Logs</a>"
}
# Function upload logs to my own server paste
function paste() {
        cat build.log | curl -F 'chips=<-' https://chipslogs.herokuapp.com > link
        HASIL="$(cat link)"
}
# Fin Error
function finerr() {
	paste
        curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
			-d chat_id="$chat_id" \
			-d "disable_web_page_preview=true" \
			-d "parse_mode=markdown" \
			-d text="Job Baking Chips throw an error(s) | **Build logs** [here](${HASIL})"
        exit 1
}
# Compile plox
function compile() {
    make O=out ARCH="${ARCH}" "${DEFCONFIG}"
    make -j"${PROCS}" O=out \
        ARCH=arm64 \
        AR=ar \
        NM=nm \
        OBJCOPY=objcopy \
        OBJDUMP=objdump \
        STRIP=strip \
        CC=gcc \
        CROSS_COMPILE=aarch64-linux-gnu- \
        CROSS_COMPILE_ARM32=arm-linux-gnueabi
	CONFIG_DEBUG_SECTION_MISMATCH=y \
        CONFIG_NO_ERROR_ON_MISMATCH=y   2>&1 | tee error.log
	
    if ! [ -a "$IMAGE" ]; then
        finderr
        exit 1
    fi

    git clone --depth=1 https://github.com/malkist01/anykernel3.git AnyKernel -b master
    cp out/arch/arm64/boot/Image.gz-dtb AnyKernel
}
# Zipping
zipping() {
    cd AnyKernel || exit 1
    zip -r9 Teletubies-"${CODENAME}"-"${DATE}".zip ./*
    cd ..
}
sticker
sendpriv
sendinfo
compile
zipping
END=$(date +"%s")
DIFF=$(($END - $START))
push
