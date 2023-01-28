const initCanvas = (id) => {
    return new fabric.Canvas('canvas', {
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 'rgba(250,250,250,1)'
    });
}

const canvas = initCanvas('canvas');