/* =========================================================
   DRAWAI 3D VIEWER
========================================================= */

let scene;
let camera;
let renderer;
let model;

init();

animate();

/* =========================================================
   INIT
========================================================= */

function init(){

    /* ================= SCENE ================= */

    scene = new THREE.Scene();

    scene.background =
        new THREE.Color(0x0b1020);

    /* ================= CAMERA ================= */

    camera =
        new THREE.PerspectiveCamera(

            60,

            window.innerWidth /
            window.innerHeight,

            0.1,

            1000
        );

    camera.position.set(0,2,5);

    /* ================= RENDERER ================= */

    renderer =
        new THREE.WebGLRenderer({

            antialias:true
        });

    renderer.setSize(

        window.innerWidth,

        window.innerHeight
    );

    renderer.outputColorSpace =
        THREE.SRGBColorSpace;

    document.body.appendChild(
        renderer.domElement
    );

    /* ================= LIGHTS ================= */

    const ambientLight =
        new THREE.AmbientLight(
            0xffffff,
            2
        );

    scene.add(ambientLight);

    const directionalLight =
        new THREE.DirectionalLight(
            0xffffff,
            3
        );

    directionalLight.position.set(
        5,
        10,
        7
    );

    scene.add(directionalLight);

    /* ================= CONTROLS ================= */

    const controls =
        new THREE.OrbitControls(

            camera,

            renderer.domElement
        );

    controls.enableDamping = true;

    /* =====================================================
       GET MODEL NAME
    ===================================================== */

    const params =
        new URLSearchParams(
            window.location.search
        );

    const modelName =
        params.get("model");

    console.log(
        "MODEL:",
        modelName
    );

    if(!modelName){

        alert("No model found");

        return;
    }

    /* =====================================================
       MODEL URL
    ===================================================== */

    const modelUrl =

        "http://127.0.0.1:5000/generated_3d/" +

        modelName;

    console.log(
        "MODEL URL:",
        modelUrl
    );

    /* =====================================================
       LOAD MODEL
    ===================================================== */

    const loader =
        new THREE.GLTFLoader();

    loader.load(

        modelUrl,

        function(gltf){

            model = gltf.scene;

            scene.add(model);

            /* CENTER MODEL */

            const box =
                new THREE.Box3()
                .setFromObject(model);

            const center =
                box.getCenter(
                    new THREE.Vector3()
                );

            model.position.sub(center);

            /* SCALE */

            const size =
                box.getSize(
                    new THREE.Vector3()
                ).length();

            const scale =
                3 / size;

            model.scale.setScalar(scale);

            console.log(
                "MODEL LOADED SUCCESSFULLY"
            );

            /* HIDE LOADER */

            const loading =
                document.getElementById(
                    "loadingScreen"
                );

            if(loading){

                loading.style.display =
                    "none";
            }
        },

        function(xhr){

            console.log(

                (
                    xhr.loaded /
                    xhr.total
                ) * 100 +

                "% loaded"
            );
        },

        function(error){

            console.error(error);

            alert(
                "Failed to load model"
            );
        }
    );

    /* =====================================================
       RESIZE
    ===================================================== */

    window.addEventListener(

        "resize",

        onWindowResize
    );
}

/* =========================================================
   RESIZE
========================================================= */

function onWindowResize(){

    camera.aspect =

        window.innerWidth /

        window.innerHeight;

    camera.updateProjectionMatrix();

    renderer.setSize(

        window.innerWidth,

        window.innerHeight
    );
}

/* =========================================================
   ANIMATE
========================================================= */

function animate(){

    requestAnimationFrame(
        animate
    );

    if(model){

        model.rotation.y += 0.003;
    }

    renderer.render(
        scene,
        camera
    );
}