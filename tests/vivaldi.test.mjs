import test from 'node:test';
import assert from 'node:assert/strict';
import { tracks,seasons,layout,shopStop,stops } from '../src/data.ts';
import { blocked } from '../src/navigation.ts';
import { readFile } from 'node:fs/promises';

test('the complete reference catalog has 12 movements and 8 additional recordings',()=>{
  assert.equal(tracks.length,20);
  assert.equal(tracks.filter(t=>!t.additional).length,12);
  assert.equal(tracks.filter(t=>t.additional).length,8);
  assert.equal(new Set(tracks.map(t=>t.src)).size,20);
  for(const season of seasons){
    assert.deepEqual(tracks.filter(t=>t.season===season.id&&!t.additional).map(t=>t.movement),[1,2,3]);
    assert.ok(tracks.some(t=>t.season===season.id&&t.additional));
  }
});
test('main and additional recordings retain the different source licenses',()=>{
  for(const track of tracks){assert.equal(track.license,track.additional?'CC BY-NC 4.0':'CC BY-SA 4.0');assert.ok(track.source.includes('classicals.de'));assert.ok(track.downloadSource.startsWith('https://www.classicals.de/s/'));}
});
test('the expanded hall has physical space for every season and safe arrival points',()=>{
  assert.equal(layout.width*layout.length,1408);
  assert.ok(layout.area>2*18*33);
  assert.equal(layout.seasons.flatMap(s=>s.paintings).length,12);
  assert.equal(stops.length,6);assert.equal(shopStop,5);
  for(const season of layout.seasons){
    const [x,,z]=season.position;
    assert.equal(blocked(x,z),false);
    assert.ok(z>layout.bounds.minZ&&z<layout.bounds.maxZ);
    for(const art of season.paintings){assert.ok(Math.abs(art.position[0])<layout.width/2);assert.ok(Math.abs(art.position[2])<layout.length/2);}
  }
});
test('the exported Blender model contains the promised gallery capacity and all movement exhibits',async()=>{
  const bytes=await readFile(new URL('../public/models/vivaldi-four-seasons.glb',import.meta.url));
  assert.equal(bytes.toString('ascii',0,4),'glTF');
  const length=bytes.readUInt32LE(12),model=JSON.parse(bytes.toString('utf8',20,20+length));
  assert.equal(model.scenes[0].extras.gallery_area_m2,layout.area);
  assert.equal(model.scenes[0].extras.recording_capacity,tracks.length);
  const movements=model.nodes.filter(node=>node.name?.startsWith('Exhibit_Vivaldi_'));
  assert.equal(movements.length,12);
  assert.equal(new Set(movements.map(node=>node.extras.track)).size,12);
  assert.equal(model.nodes.filter(node=>node.name?.startsWith('Exhibit_Interpretations_')).length,4);
});
