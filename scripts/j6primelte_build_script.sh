#!/usr/bin/env bash

# Dependencies
rm -rf kernel
git clone $REPO -b $BRANCH kernel 
cd kernel

#!/bin/bash

# this script installs GCC 4.9.4 
# to use it navigate to your home directory and type:
# sh install-gcc-4.9.4.sh

# download and install gcc 4.9.4
wget https://ftp.gnu.org/gnu/gcc/gcc-4.9.4/gcc-4.9.4.tar.gz
tar xzf gcc-4.9.4.tar.gz
cd gcc-4.9.4
./contrib/download_prerequisites
cd ..
mkdir objdir

cd objdir
../gcc-4.9.4/configure --prefix=$HOME/gcc-4.9.4 --enable-languages=c,c++,fortran,go --disable-multilib
make

# install
make install

# clean up
rm -rf ~/objdir
rm -f ~/gcc-4.9.4.tar.gz

# add to path (you may want to add these lines to $HOME/.bash_profile)
export PATH=$HOME/gcc-4.9.4/bin:$PATH
export LD_LIBRARY_PATH=$HOME/gcc-4.9.4/lib:$HOME/gcc-4.9.4/lib64:$LD_LIBRARY_PATH
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
