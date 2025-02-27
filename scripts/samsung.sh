#!/usr/bin/env bash

# Dependencies
rm -rf kernel
git clone $REPO -b $BRANCH kernel
cd kernel

echo "Cloning dependencies"
git clone https://github.com/najahiiii/aarch64-linux-gnu.git -b 4.9-mirror --depth=1 gcc
git clone https://github.com/najahiiii/aarch64-linux-gnu.git -b 4.9-32-mirror --depth=1 gcc32
echo "Done"
GCC="$(pwd)/gcc/bin/aarch64-linux-android-"
GCC32="$(pwd)/gcc32/bin/arm-linux-androideabi-"
tanggal=$(TZ=Asia/Jakarta date +'%H%M-%d%m%y')
START=$(date +"%s")
IMAGE=$(pwd)/out/arch/arm64/boot/Image.gz-dtb
KERNEL_DIR=$(pwd)
export ARCH=arm64
export KBUILD_COMPILER_STRING
export KBUILD_BUILD_USER=malkist
export KBUILD_BUILD_HOST=android
DEVICE="samsung"
export DEVICE
CODENAME="j6primelte"
export CODENAME
# sticker plox
function sticker() {
        curl -s -X POST "https://api.telegram.org/bot$token/sendSticker" \
                        -d sticker="CAADBQADJgEAAkMQsyKKVBNIRBu80wI" \
                        -d chat_id=$chat_id
}
# Send info plox channel
function sendinfo() {
        curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
                        -d chat_id=$chat_id \
                        -d "disable_web_page_preview=true" \
                        -d "parse_mode=html" \
                        -d text="<b>ChipsKernel CAF</b> CI Triggered%0ABuild started on <code>Drone CI/CD</code>%0AFor device <b>Xiaomi Redmi 4A/5A (Rolex/Riva)</b>%0Abranch <code>$(git rev-parse --abbrev-ref HEAD)</code> (Android 9.0/Pie)%0AUnder commit <code>$(git log --pretty=format:'"%h : %s"' -1)</code>%0AUsing compiler: <code>$(${GCC}gcc --version | head -n 1 | perl -pe 's/\(http.*?\)//gs' | sed -e 's/  */ /g')</code>%0AStarted on <code>$(TZ=Asia/Jakarta date)</code>%0A<b>Build Status:</b> #Stable"
}
# Send private info
function sendpriv() {
        curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
                        -d chat_id=$priv_id \
                        -d "disable_web_page_preview=true" \
                        -d "parse_mode=html" \
                        -d text="ChipsKernel CI Started%0ADrone triggered by: <code>${DRONE_BUILD_EVENT}</code> event%0AJob name: <code>Baking</code>%0ACommit point: <a href='${DRONE_COMMIT_LINK}'>$(git log --pretty=format:'"%h : %s"' -1)</a>%0A<b>Pipeline jobs</b> <a href='https://cloud.drone.io/najahiiii/moaikernal/${DRONE_BUILD_NUMBER}'>here</a>"
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
        make -s -C $(pwd) O=out teletubies_defconfig
        make -C $(pwd) CROSS_COMPILE="${GCC}" CROSS_COMPILE_ARM32="${GCC32}" O=out -j32 -l32 2>&1| tee build.log
        
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
