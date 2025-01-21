#!/usr/bin/env bash

# Dependencies
rm -rf kernel
git clone $REPO -b $BRANCH kernel 
cd kernel

clang() {
    rm -rf clang
    echo "Cloning gcc"
    if [ ! -d "gcc" ]; then
        git clone -q https://github.com/xiangfeidexiaohuo/GCC-4.9.git --depth=1 -b gcc4.9
        KBUILD_COMPILER_STRING="GCC 4.9"
        PATH="${PWD}/gçc/bin:${PATH}"
    fi
    sudo apt install -y ccache
    echo "Done"
}

IMAGE=$(pwd)/out/arch/arm64/boot/Image.gz-dtb
IMAGE2=$(pwd)/out/arch/arm64/boot/dtbo.img
DATE=$(date +"%Y%m%d-%H%M")
START=$(date +"%s")
KERNEL_DIR=$(pwd)
CACHE=1
export CACHE
export KBUILD_COMPILER_STRING
ARCH=arm64
export ARCH
KBUILD_BUILD_HOST="android-server"
export KBUILD_BUILD_HOST
KBUILD_BUILD_USER="malkist"
export KBUILD_BUILD_USER
DEVICE="Samsung J6+"
export DEVICE
CODENAME="j6primelte"
export CODENAME
DEFCONFIG="j6primelte_defconfig"
export DEFCONFIG
COMMIT_HASH=$(git rev-parse --short HEAD)
export COMMIT_HASH
PROCS=$(nproc --all)
export PROCS
STATUS=TEST
export STATUS
source "${HOME}"/.bashrc && source "${HOME}"/.profile
if [ $CACHE = 1 ]; then
    ccache -M 100G
    export USE_CCACHE=1
fi

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

# Compile
compile() {

    if [ -d "out" ]; then
        rm -rf out && mkdir -p out
    fi

    make O=out ARCH="${ARCH}" "${DEFCONFIG}"
    make -j"${PROCS}" O=out \
        ARCH=arm64 \
        CROSS_COMPILE=aarch64-linux-gnu- \
        CROSS_COMPILE_ARM32=arm-linux-gnueabi

    if ! [ -a "$IMAGE" ]; then
        exit 1
    fi

    git clone --depth=1 -b master https://github.com/RooGhz720/Anykernel3.git AnyKernel
    cp out/arch/arm64/boot/Image.gz-dtb AnyKernel
    cp out/arch/arm64/boot/dtbo.img AnyKernel
    cp out/arch/arm64/boot/dtb.img AnyKernel
}
# Zipping
zipping() {
    cd AnyKernel || exit 1
    zip -r9 Test-Build-Kernel-"${BRANCH}"-"${CODENAME}"-"${DATE}".zip ./*
    cd ..
}

clang
sendinfo
compile
zipping
END=$(date +"%s")
DIFF=$((END - START))
push
