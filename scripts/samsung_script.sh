#!/usr/bin/env bash

# Dependencies
rm -rf kernel
git clone $REPO -b $BRANCH kernel 
cd kernel

clang() {
    rm -rf clang
    echo "Cloning clang"
    if [ ! -d "clang" ]; then
        git clone https://gitlab.com/LeCmnGend/proton-clang -b clang-13 --depth=1 clang
        KBUILD_COMPILER_STRING="Proton clang 13.0 x sirnewbies"
        PATH="${PWD}/clang/bin:${PATH}"
    fi
    sudo apt install -y ccache
    echo "Done"
}

IMAGE=$(pwd)/out/arch/arm/boot/zImage-dtb
DATE=$(date +"%Y%m%d-%H%M")
START=$(date +"%s")
KERNEL_DIR=$(pwd)
CACHE=1
export CACHE
export KBUILD_COMPILER_STRING
ARCH=arm6
export ARCH
KBUILD_BUILD_HOST="android"
export KBUILD_BUILD_HOST
KBUILD_BUILD_USER="malkist"
export KBUILD_BUILD_USER
DEVICE="samsung"
export DEVICE
CODENAME="a7xelte"
export CODENAME
DEFCONFIG="j6primelte_defconfig"
export DEFCONFIG
COMMIT_HASH=$(git rev-parse --short HEAD)
export COMMIT_HASH
PROCS=$(nproc --all)
export PROCS
STATUS=STABLE
export STATUS
source "${HOME}"/.bashrc && source "${HOME}"/.profile
if [ $CACHE = 1 ]; then
    ccache -M 100G
    export USE_CCACHE=1
fi
LC_ALL=C
export LC_ALL

tg() {
    curl -sX POST https://api.telegram.org/bot"${token}"/sendMessage -d chat_id="${chat_id}" -d parse_mode=Markdown -d disable_web_page_preview=true -d text="$1" &>/dev/null
}

tgs() {
    MD5=$(md5sum "$1" | cut -d' ' -f1)
    curl -fsSL -X POST -F document=@"$1" https://api.telegram.org/bot"${token}"/sendDocument \
        -F "chat_id=${chat_id}" \
        -F "parse_mode=Markdown" \
        -F "caption=$2 | *MD5*: \`$MD5\`"
}

# Send Build Info
sendinfo() {
    tg "
• sirCompiler Action •
*Building on*: \`Github actions\`
*Date*: \`${DATE}\`
*Device*: \`${DEVICE} (${CODENAME})\`
*Branch*: \`$(git rev-parse --abbrev-ref HEAD)\`
*Last Commit*: [${COMMIT_HASH}](${REPO}/commit/${COMMIT_HASH})
*Compiler*: \`${KBUILD_COMPILER_STRING}\`
*Build Status*: \`${STATUS}\`"
}

# Push kernel to channel
push() {
    cd AnyKernel || exit 1
    ZIP=$(echo *.zip)
    tgs "${ZIP}" "Build took $((DIFF / 60)) minute(s) and $((DIFF % 60)) second(s). | For *${DEVICE} (${CODENAME})* | ${KBUILD_COMPILER_STRING}"
}

# Catch Error
finderr() {
    curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
        -d chat_id="$chat_id" \
        -d "disable_web_page_preview=true" \
        -d "parse_mode=markdown" \
        -d sticker="CAACAgIAAxkBAAED3JViAplqY4fom_JEexpe31DcwVZ4ogAC1BAAAiHvsEs7bOVKQsl_OiME" \
        -d text="Build throw an error(s)"
    error_sticker
    exit 1
}

# Compile
compile() {

    if [ -d "out" ]; then
        rm -rf out && mkdir -p out
    fi

    make -C=out ARCH="${ARCH}" "${DEFCONFIG}"
    make -j64 -C "${PROCS}" O=out \
        ARCH=$ARCH \
        CC="clang" \
        LLVM=1 \
        CROSS_COMPILE_ARM32=arm-linux-gnueabi-

    if ! [ -a "$IMAGE" ]; then
        finderr
        exit 1
    fi

        git clone --depth=1 https://github.com/malkist01/anykernel3.git AnyKernel AnyKernel -b master
    cp out/arch/arm/boot/Image AnyKernel
}
# Zipping
zipping() {
    cd AnyKernel || exit 1
    zip -r9 Teletubies-Kernel-"${BRANCH}"-"${CODENAME}"-"${DATE}".zip ./*
    cd ..
}

clang
sendinfo
compile
zipping
END=$(date +"%s")
DIFF=$((END - START))
push
