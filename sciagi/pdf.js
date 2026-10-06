const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage();
  await p.goto('file://'+process.argv[2]); await p.waitForTimeout(500);
  const ov=await p.$$eval('.page',ps=>ps.map(pg=>[...pg.querySelectorAll('.col')].map(c=>[c.scrollHeight,pg.clientHeight])));
  console.log(JSON.stringify(ov));
  await p.pdf({path:process.argv[3],format:'A4',printBackground:true,margin:{top:'8mm',bottom:'8mm',left:'8mm',right:'8mm'}});
  await b.close();
})();
