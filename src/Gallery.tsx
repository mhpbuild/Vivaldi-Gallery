import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { Reflector } from 'three/examples/jsm/objects/Reflector.js';
import { ArrowDown, ArrowLeft, ArrowRight, ArrowUp } from 'lucide-react';
import { walkStep } from './navigation';
import { layout, shopStop } from './data';

type Props={stop:number;viewVersion:number;entered:boolean;playing:boolean;onStop:(stop:number)=>void;onTrack:(index:number)=>void;onWalk:()=>void};
const views=[layout.entrance,...layout.seasons.map(s=>({position:s.position,target:s.target})),{position:layout.shop.view,target:layout.shop.target}];

const vector=(p:number[])=>new THREE.Vector3(p[0],p[1],p[2]);

export default function Gallery({stop,viewVersion,entered,playing,onStop,onTrack,onWalk}:Props){
  const host=useRef<HTMLDivElement>(null);
  const state=useRef({stop,viewVersion,entered,playing,onStop,onTrack,onWalk});
  state.current={stop,viewVersion,entered,playing,onStop,onTrack,onWalk};
  const touch=useRef({forward:0,strafe:0});
  const [progress,setProgress]=useState(0),[ready,setReady]=useState(false),[error,setError]=useState(false);
  useEffect(()=>{
    const container=host.current;if(!container)return;
    let renderer:THREE.WebGLRenderer;
    try{renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});}catch{setError(true);return;}
    renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));
    renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
    renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
    renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('aria-label','Jelajah museum 3D. W A S D atau panah untuk berjalan. Seret untuk melihat.');
    container.appendChild(renderer.domElement);
    const scene=new THREE.Scene();scene.background=new THREE.Color('#29291f');scene.fog=new THREE.Fog('#24241e',45,110);
    const camera=new THREE.PerspectiveCamera(58,1,.08,100);camera.position.copy(vector(views[0].position));camera.lookAt(vector(views[0].target));
    const look=vector(views[0].target),direction=new THREE.Vector3();
    const reduced=matchMedia('(prefers-reduced-motion: reduce)');
    const pmrem=new THREE.PMREMGenerator(renderer),environmentScene=new RoomEnvironment();
    const environment=pmrem.fromScene(environmentScene,.04);scene.environment=environment.texture;scene.environmentIntensity=.4;environmentScene.dispose();
    scene.add(new THREE.AmbientLight('#e2cba1',.65));scene.add(new THREE.HemisphereLight('#e8ddc6','#594735',.9));
    const lights:THREE.Light[]=[];
    for(const z of layout.seasons.map(s=>s.center)){
      const light=new THREE.PointLight('#ffdfac',95,23,2);light.position.set(0,6.7,z);scene.add(light);lights.push(light);
      if(z===layout.seasons[0].center){light.castShadow=true;light.shadow.mapSize.set(innerWidth<700?512:1024,innerWidth<700?512:1024);light.shadow.bias=-.0005;light.shadow.normalBias=.025;}
    }
    function spot(position:number[],target:number[],power:number,angle=.65){
      const light=new THREE.SpotLight('#ffddb0',power,15,angle,.65,2);light.position.copy(vector(position));light.target.position.copy(vector(target));scene.add(light,light.target);lights.push(light);
    }
    for(const x of [-8.5,8.5])for(const z of layout.seasons.map(s=>s.center))spot([x,5.9,z],[Math.sign(x)*10.4,3.4,z],80,.65);
    spot([-3,6,27],[0,2.5,24],170,.72);
    let disposed=false,model:THREE.Group|undefined,dirty=true;
    const floorReflection=new Reflector(new THREE.PlaneGeometry(21.5,63.5),{textureWidth:innerWidth<700?512:1024,textureHeight:512,color:0x8c8272,clipBias:.003,multisample:0});
    floorReflection.rotation.x=-Math.PI/2;floorReflection.position.y=.078;const reflectionMaterial=floorReflection.material as THREE.ShaderMaterial;reflectionMaterial.transparent=true;reflectionMaterial.depthWrite=false;
    reflectionMaterial.fragmentShader=reflectionMaterial.fragmentShader.replace('#include <tonemapping_fragment>','gl_FragColor.a = 0.055;\n#include <tonemapping_fragment>');scene.add(floorReflection);
    new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).load('/models/vivaldi-four-seasons.glb',gltf=>{
      if(disposed){disposeObject(gltf.scene);return;}
      model=gltf.scene;
      model.traverse(object=>{if(object instanceof THREE.Mesh){
        object.castShadow=true;object.receiveShadow=true;
        const original=object.material as THREE.MeshStandardMaterial;
        if(original.name==='Coffer recess pigment'){object.material=new THREE.MeshStandardMaterial({color:'#9b835d',roughness:.95,envMapIntensity:.2});object.receiveShadow=false;}
        else if(original.name.startsWith('Vivaldi Artwork')||original.name.startsWith('Vivaldi Portrait')){if(original.map)original.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());object.material=new THREE.MeshBasicMaterial({map:original.map,color:'#e2d8c2'});}
        else if(object.userData.cycles_baked&&original.emissiveMap){const baked=original.emissiveMap;baked.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());object.material=new THREE.MeshBasicMaterial({map:baked});}

      }});
      scene.add(model);dirty=true;setReady(true);setProgress(100);
    },event=>{if(event.total)setProgress(Math.round(event.loaded/event.total*100));},()=>{if(!disposed)setError(true);});

    // Shop picking target is invisible but participates in raycasting.
    const shopTarget=new THREE.Mesh(new THREE.BoxGeometry(3.7,4,3.6),new THREE.MeshBasicMaterial({visible:false}));shopTarget.position.set(layout.shop.position[0],2,layout.shop.position[2]+.5);shopTarget.userData.zone=shopStop;scene.add(shopTarget);
    const interpretationTargets=layout.seasons.map((season,index)=>{const target=new THREE.Mesh(new THREE.BoxGeometry(3.1,1.5,1.85),new THREE.MeshBasicMaterial({visible:false}));target.position.set(6.4,.8,season.center+3.4);target.userData.zone=index+1;scene.add(target);return target;});
    let manual=false,yaw=0,pitch=0,lastView=-1,dragging=false,moved=0,lastX=0,lastY=0,startX=0,startY=0;
    const keys=new Set<string>();
    function beginManual(){
      if(manual)return;
      camera.getWorldDirection(direction);yaw=Math.atan2(-direction.x,-direction.z);pitch=Math.asin(Math.max(-1,Math.min(1,direction.y)));
      manual=true;camera.position.y=1.72;state.current.onWalk();dirty=true;
    }
    const editable=(target:EventTarget|null)=>target instanceof HTMLElement&&(target.isContentEditable||['INPUT','TEXTAREA','SELECT'].includes(target.tagName));
    const keyDown=(event:KeyboardEvent)=>{
      if(!state.current.entered||document.querySelector('dialog[open]')||editable(event.target)||event.metaKey||event.ctrlKey||event.altKey)return;
      const key=event.key.toLowerCase();if(key==='shift'){keys.add(key);return;}if(['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright'].includes(key)){event.preventDefault();keys.add(key);beginManual();}
    };
    const keyUp=(event:KeyboardEvent)=>keys.delete(event.key.toLowerCase());
    const resetKeys=()=>{keys.clear();touch.current={forward:0,strafe:0};dragging=false;};
    const down=(event:PointerEvent)=>{
      if(!state.current.entered)return;renderer.domElement.focus({preventScroll:true});dragging=true;moved=0;startX=lastX=event.clientX;startY=lastY=event.clientY;renderer.domElement.setPointerCapture(event.pointerId);
    };
    const move=(event:PointerEvent)=>{
      if(!dragging)return;const dx=event.clientX-lastX,dy=event.clientY-lastY;moved=Math.hypot(event.clientX-startX,event.clientY-startY);
      if(moved>5){beginManual();yaw-=dx*.003;pitch=Math.max(-1.05,Math.min(1.05,pitch-dy*.003));dirty=true;}
      lastX=event.clientX;lastY=event.clientY;
    };
    const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
    const pointerUp=(event:PointerEvent)=>{
      if(!dragging)return;dragging=false;if(moved>6||!model)return;
      const bounds=renderer.domElement.getBoundingClientRect();pointer.set((event.clientX-bounds.left)/bounds.width*2-1,-(event.clientY-bounds.top)/bounds.height*2+1);raycaster.setFromCamera(pointer,camera);
      const hits=raycaster.intersectObjects([model,shopTarget,...interpretationTargets],true);
      for(const hit of hits){if(hit.object.userData.track!==undefined){state.current.onTrack(hit.object.userData.track);break;}if(hit.object.userData.zone!==undefined){state.current.onStop(hit.object.userData.zone);break;}if(hit.distance>.1)break;}
    };
    const cancel=()=>{dragging=false;};
    window.addEventListener('keydown',keyDown);window.addEventListener('keyup',keyUp);window.addEventListener('blur',resetKeys);
    document.addEventListener('visibilitychange',resetKeys);
    renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',pointerUp);renderer.domElement.addEventListener('pointercancel',cancel);
    const lost=(event:Event)=>{event.preventDefault();setError(true);};renderer.domElement.addEventListener('webglcontextlost',lost);
    const resize=()=>{const bounds=container.getBoundingClientRect();renderer.setSize(bounds.width,bounds.height);camera.aspect=bounds.width/bounds.height;camera.fov=bounds.width<600?70:58;camera.updateProjectionMatrix();dirty=true;};
    const observer=new ResizeObserver(resize);observer.observe(container);resize();
    let frame=0,last=0,lastDomUpdate=0;
    const draw=(time:number)=>{
      const dt=Math.min((time-last)/1000,.05);last=time;const s=state.current;
      if(lastView!==s.viewVersion){manual=false;keys.clear();touch.current={forward:0,strafe:0};lastView=s.viewVersion;dirty=true;}
      if(document.querySelector('dialog[open]'))resetKeys();
      if(manual){
        const forward=(keys.has('w')||keys.has('arrowup')?1:0)-(keys.has('s')||keys.has('arrowdown')?1:0)+touch.current.forward;
        const strafe=(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0)+touch.current.strafe;
        if(forward||strafe){const p=walkStep({x:camera.position.x,z:camera.position.z},{forward,strafe,yaw,delta:dt,fast:keys.has('shift')});camera.position.x=p.x;camera.position.z=p.z;dirty=true;}
        camera.rotation.set(pitch,yaw,0,'YXZ');
      }else{
        const view=views[s.stop];const pos=vector(view.position),target=vector(view.target);
        if(camera.position.distanceToSquared(pos)>1e-7||look.distanceToSquared(target)>1e-7){const alpha=reduced.matches?1:1-Math.exp(-dt*4);camera.position.lerp(pos,alpha);look.lerp(target,alpha);camera.lookAt(look);dirty=true;}
      }
      if((touch.current.forward||touch.current.strafe)&&!manual)beginManual();
      if(time-lastDomUpdate>150){container.dataset.cameraPosition=`${camera.position.x.toFixed(3)},${camera.position.y.toFixed(3)},${camera.position.z.toFixed(3)}`;container.dataset.navigationMode=manual?'walk':'guided';lastDomUpdate=time;}
      if(dirty&&document.visibilityState==='visible'){renderer.render(scene,camera);dirty=false;}
      frame=requestAnimationFrame(draw);
    };frame=requestAnimationFrame(draw);
    function disposeObject(object:THREE.Object3D){object.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material]){for(const value of Object.values(m))if(value instanceof THREE.Texture)value.dispose();m.dispose();}}});}
    return()=>{disposed=true;cancelAnimationFrame(frame);observer.disconnect();window.removeEventListener('keydown',keyDown);window.removeEventListener('keyup',keyUp);window.removeEventListener('blur',resetKeys);document.removeEventListener('visibilitychange',resetKeys);renderer.domElement.removeEventListener('pointerdown',down);renderer.domElement.removeEventListener('pointermove',move);renderer.domElement.removeEventListener('pointerup',pointerUp);renderer.domElement.removeEventListener('pointercancel',cancel);renderer.domElement.removeEventListener('webglcontextlost',lost);disposeObject(scene);floorReflection.getRenderTarget().dispose();environment.dispose();pmrem.dispose();renderer.dispose();renderer.domElement.remove();};
  },[]);
  function touchMove(forward:number,strafe:number){touch.current={forward,strafe};}
  const directions=[
    {forward:1,strafe:0,label:'Berjalan maju',Icon:ArrowUp},
    {forward:0,strafe:-1,label:'Berjalan ke kiri',Icon:ArrowLeft},
    {forward:-1,strafe:0,label:'Berjalan mundur',Icon:ArrowDown},
    {forward:0,strafe:1,label:'Berjalan ke kanan',Icon:ArrowRight}
  ];
  const control=(d:typeof directions[number])=><button key={d.label} aria-label={d.label}
    onPointerDown={e=>{e.currentTarget.setPointerCapture(e.pointerId);touchMove(d.forward,d.strafe);}}
    onPointerUp={()=>touchMove(0,0)} onPointerCancel={()=>touchMove(0,0)}
    onKeyDown={e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();touchMove(d.forward,d.strafe);}}}
    onKeyUp={()=>touchMove(0,0)} onBlur={()=>touchMove(0,0)}><d.Icon size={18}/></button>;
  return <>
    <div ref={host} className="gallery-scene can-drag">
      {!ready&&!error&&<div className="museum-loading"><span className="loading-ring"/><span>Memasuki dunia Vivaldi<small>MENYIAPKAN MUSEUM BLENDER · {progress}%</small></span></div>}
      {error&&<div className="scene-status"><strong>Model museum belum dapat dimuat.</strong><p>Anda tetap dapat membuka koleksi musik dan toko suvenir melalui navigasi.</p><button onClick={()=>location.reload()}>Muat ulang museum</button></div>}
    </div>
    {entered&&ready&&<div className="walk-controls" aria-label="Kontrol berjalan">{control(directions[0])}<div>{directions.slice(1).map(control)}</div></div>}
  </>;
}
