import catalog from './catalog.json' with { type: 'json' };
import layout from './layout.json' with { type: 'json' };
export { layout };
export type Track = { id:string; title:string; artist:string; composer?:string; genre:string; duration:string; seconds?:number; src:string; color:string; description:string; source?:string; license:string; local?:boolean; season?:string; movement?:number; tempo?:string; art?:string; artPanel?:number; downloadSource?:string; additional?:boolean; originalTitle?:string };
export const tracks: Track[] = catalog.tracks;
export const seasons = catalog.seasons;
export const recordingCredits = { violin:'John Harrison', conductor:'Robert Turizziani', ensemble:'The Wichita State University Chamber Players', venue:'Wiedemann Recital Hall, Wichita State University', source:'https://www.classicals.de/vivaldi-seasons', artist:'https://johnharrison.cc', license:'CC BY-SA 4.0', licenseUrl:'https://creativecommons.org/licenses/by-sa/4.0/' };
export const totalDuration = tracks.reduce((sum,track)=>sum+(track.seconds||0),0);
export const shopStop = seasons.length + 1;
export type Product = { id: string; name: string; type: string; price: number; color: string; detail: string };
export const products: Product[] = [
  { id:'tote', name:'Le Quattro Stagioni Tote', type:'TOTE BAG', price:145000, color:'#ded3b9', detail:'Kanvas natural · 38 × 42 cm' },
  { id:'record', name:'Vivaldi · Collector’s Sleeve', type:'VINYL ART', price:285000, color:'#c84629', detail:'Objek suvenir fiktif · 12 inci' },
  { id:'poster', name:'The Four Seasons Print', type:'ART PRINT', price:95000, color:'#54685c', detail:'Cetak ilustrasi · A3' }
];
export type Cart = Record<string, number>;
export function changeQuantity(cart: Cart, id: string, amount: number): Cart {
  if (!products.some(product=>product.id===id)) return cart;
  const next = { ...cart, [id]: Math.max(0, Math.min(20, (cart[id] || 0) + amount)) };
  if (!next[id]) delete next[id];
  return next;
}
export const cartTotal = (cart: Cart) => products.reduce((sum,p)=>sum+p.price*(cart[p.id]||0),0);
export const rupiah = (value: number) => new Intl.NumberFormat('id-ID',{style:'currency',currency:'IDR',maximumFractionDigits:0}).format(value);
export const stops = ['Atrio Vivaldi', ...seasons.map(s=>s.name), 'Bottega'];
