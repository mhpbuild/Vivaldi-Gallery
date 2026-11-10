import layout from './layout.json' with { type: 'json' };
export type Position = { x:number; z:number };
export type WalkInput = { forward:number; strafe:number; yaw:number; delta:number; fast?:boolean };
// Walkable hall limits and the footprints of physical exhibits, benches and shop.
export const obstacles = [
  {minX:-1.65,maxX:1.65,minZ:22.7,maxZ:25.3},
  {minX:5.2,maxX:9.0,minZ:28.3,maxZ:31.2},
  ...layout.seasons.flatMap(({center})=>[
    {minX:4.8,maxX:6.6,minZ:center-2.5,maxZ:center+.9},
    {minX:-6.6,maxX:-4.8,minZ:center-2.5,maxZ:center+.9},
    {minX:4.65,maxX:8.15,minZ:center+2.3,maxZ:center+4.5}
  ])
];
export function blocked(x:number,z:number){return obstacles.some(o=>x>o.minX&&x<o.maxX&&z>o.minZ&&z<o.maxZ);}
export function walkStep(position:Position,input:WalkInput):Position{
  const length=Math.hypot(input.forward,input.strafe);
  if(!length)return position;
  const speed=(input.fast?4.8:2.7)*Math.min(input.delta,.05)/Math.max(1,length);
  const dx=(-Math.sin(input.yaw)*input.forward+Math.cos(input.yaw)*input.strafe)*speed;
  const dz=(-Math.cos(input.yaw)*input.forward-Math.sin(input.yaw)*input.strafe)*speed;
  const x=Math.max(layout.bounds.minX,Math.min(layout.bounds.maxX,position.x+dx));
  const safeX=blocked(x,position.z)?position.x:x;
  const z=Math.max(layout.bounds.minZ,Math.min(layout.bounds.maxZ,position.z+dz));
  return {x:safeX,z:blocked(safeX,z)?position.z:z};
}
