export const WEIGHTS = Object.freeze({family:40,weather:20,occasion:20,intensity:5,budget:15});
export const FAMILIES = ['woody','amber','vanilla','fresh','citrus','floral','leather','spicy','gourmand','aquatic'];
export const WEATHER = ['hot','mild','cool','cold'];
export const OCCASIONS = ['office','daily','date night','evening','special events'];
export const RESULT_COUNT = 5;
export const MAX_RECOMMENDATIONS_PER_BRAND = 3;

export function budgetLimit(answers) {
  if (!Number.isFinite(answers.budget) || answers.budget < 0) throw new Error('Budget must be a non-negative number.');
  return Math.round(answers.budget * 1.2 * 100) / 100;
}

const CLIMATE_ORDER = WEATHER;
const OCCASION_NEARNESS = Object.freeze({
  office:{office:1,daily:.75,'date night':.2,evening:.15,'special events':.1},
  daily:{office:.75,daily:1,'date night':.5,evening:.35,'special events':.25},
  'date night':{office:.2,daily:.5,'date night':1,evening:.85,'special events':.7},
  evening:{office:.15,daily:.35,'date night':.85,evening:1,'special events':.9},
  'special events':{office:.1,daily:.25,'date night':.7,evening:.9,'special events':1},
});
const FAMILY_NOTE_TERMS = Object.freeze({
  woody:['wood','woody','woodsy','cedar','cedarwood','sandalwood','oud','agarwood','vetiver','patchouli','cashmeran','hinoki','cypress','pine','guaiac','guaiac wood','rosewood','oak','oakmoss','ebony','amberwood'],
  amber:['amber','amber accord','labdanum','benzoin','myrrh','resin','opoponax','storax','peru balsam','tolu balsam'],
  vanilla:['vanilla','vanillin','tonka','tonka bean'],
  fresh:['mint','basil','sage','green tea','cucumber','green notes','fresh notes','lavender','verbena','rosemary'],
  citrus:['bergamot','lemon','grapefruit','mandarin','tangerine','orange','orange peel','bitter orange','lime','yuzu','petitgrain'],
  floral:['rose','jasmine','tuberose','iris','violet','peony','lily','freesia','magnolia','orange blossom','ylang ylang','geranium','lavender','osmanthus','lilac','honeysuckle'],
  leather:['leather','suede'],
  spicy:['cardamom','pepper','cinnamon','saffron','ginger','clove','nutmeg','cumin','chili','cayenne'],
  gourmand:['chocolate','caramel','praline','coffee','cacao','cocoa','honey','sugar','almond','hazelnut','chestnut','toffee','marshmallow','whipped cream','cream accord','milk chocolate','lactonic notes'],
  aquatic:['marine','sea salt','aquatic','ozonic','sea water','seawater','oceanic','algae','calone','sea notes'],
});

const FAMILY_NOTE_EXCLUSIONS = Object.freeze({
  amber:['ambergris'],
  citrus:['orange blossom'],
  floral:['violet leaf'],
});

// Editorial scent facets derived only from notes recorded for the fragrance.
// These describe a note-led impression, not a verified performance claim.
const NOTE_VIBE_RULES = Object.freeze([
  {vibe:'warm & resinous',families:['amber'],terms:['amber','labdanum','benzoin','myrrh','resin','opoponax','storax','peru balsam','tolu balsam'],excludes:['ambergris']},
  {vibe:'creamy & sweet',families:['vanilla','gourmand'],terms:['vanilla','vanillin','tonka','caramel','praline','honey','marshmallow','whipped cream','cream accord','almond']},
  {vibe:'edible gourmand',families:['gourmand'],terms:['chocolate','cocoa','cacao','coffee','caramel','praline','toffee','sugar','marshmallow','hazelnut','chestnut']},
  {vibe:'dry & grounded woods',families:['woody','leather'],terms:['cedar','cedarwood','sandalwood','oud','agarwood','vetiver','patchouli','cashmeran','hinoki','cypress','pine','guaiac','guaiac wood','rosewood','oak','oakmoss','ebony','amberwood']},
  {vibe:'smoky & leathery',families:['leather','woody'],terms:['leather','suede','birch tar','tobacco','smoke','incense']},
  {vibe:'bright & citrus',families:['citrus','fresh'],terms:['bergamot','lemon','grapefruit','mandarin','tangerine','orange','orange peel','bitter orange','lime','yuzu','petitgrain'],excludes:['orange blossom']},
  {vibe:'green & aromatic',families:['fresh'],terms:['mint','basil','sage','green tea','cucumber','green notes','fresh notes','lavender','verbena','rosemary']},
  {vibe:'soft floral',families:['floral'],terms:['rose','jasmine','tuberose','iris','violet','peony','lily','freesia','magnolia','orange blossom','ylang ylang','geranium','osmanthus','lilac','honeysuckle'],excludes:['violet leaf']},
  {vibe:'warm spice',families:['spicy'],terms:['cardamom','pepper','cinnamon','saffron','ginger','clove','nutmeg','cumin','chili','cayenne']},
  {vibe:'breezy & mineral',families:['aquatic','fresh'],terms:['marine','sea salt','aquatic','ozonic','sea water','seawater','oceanic','algae','calone','sea notes']},
  {vibe:'juicy fruit',families:['gourmand'],terms:['raspberry','pear','apple','plum','blackcurrant','fig','peach','cherry','grape','berry','pomegranate','mango','pineapple','apricot','lychee']},
  {vibe:'soft musk',families:['woody','fresh'],terms:['musk','ambrette','white musk','skin musk']},
  {vibe:'powdery',families:['floral'],terms:['iris','orris','heliotrope','violet'],excludes:['violet leaf']},
]);

const FAMILY_VIBE_FACETS=Object.freeze(Object.fromEntries(FAMILIES.map(family=>[
  family,NOTE_VIBE_RULES.filter(rule=>rule.families.includes(family)).map(rule=>rule.vibe),
])));

const NOTE_VIBE_COMPOSITIONS=Object.freeze([
  {requires:['warm & resinous','creamy & sweet','edible gourmand'],label:'a warm, resinous gourmand with creamy sweetness'},
  {requires:['soft floral','creamy & sweet','edible gourmand'],label:'a soft, sweet floral gourmand'},
  {requires:['warm & resinous','warm spice'],label:'a warm, spiced amber profile'},
  {requires:['dry & grounded woods','smoky & leathery'],label:'dry, smoky woods with a leathered edge'},
  {requires:['bright & citrus','green & aromatic'],label:'a bright, green aromatic citrus profile'},
  {requires:['bright & citrus','soft floral'],label:'bright citrus framed by soft florals'},
  {requires:['breezy & mineral','green & aromatic'],label:'a breezy, green aquatic profile'},
  {requires:['soft floral','powdery'],label:'a soft floral profile with powdery facets'},
  {requires:['juicy fruit','creamy & sweet'],label:'juicy fruit softened by creamy sweetness'},
]);

function normalizeNote(value) {
  return String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().replace(/&/g,' and ').replace(/[^a-z0-9]+/g,' ').trim().split(/\s+/).filter(Boolean);
}

function normalizeBrand(value) {
  const normalized=String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
  if(normalized==='lattafa pride')return 'lattafa';
  if(normalized==='maison margiela fragrances')return 'maison margiela';
  return normalized;
}

function hasNotePhrase(noteWords, phrase) {
  const phraseWords=normalizeNote(phrase);
  if(!phraseWords.length||phraseWords.length>noteWords.length)return false;
  return noteWords.some((_,index)=>phraseWords.every((word,offset)=>noteWords[index+offset]===word));
}

function noteMatchesTerms(note, terms=[], excludes=[]) {
  const words=normalizeNote(note);
  if(excludes.some(term=>hasNotePhrase(words,term)))return false;
  return terms.some(term=>hasNotePhrase(words,term));
}

function familyEvidence(family, fragrance) {
  if ((fragrance.families||[]).includes(family)) return {family,kind:'family'};
  const terms=FAMILY_NOTE_TERMS[family]||[];
  const note=(fragrance.notes||[]).find(n=>noteMatchesTerms(n,terms,FAMILY_NOTE_EXCLUSIONS[family]||[]));
  return note?{family,kind:'note',note}:null;
}

function noteLedVibe(notes) {
  if(!Array.isArray(notes))return [];
  return NOTE_VIBE_RULES.flatMap(rule=>{
    const evidence=notes.filter(note=>noteMatchesTerms(note,rule.terms,rule.excludes||[]));
    return evidence.length?[{vibe:rule.vibe,families:rule.families,notes:[...new Set(evidence)]}]:[];
  });
}

function composeNoteVibe(vibeEvidence) {
  const known=new Set(vibeEvidence.map(x=>x.vibe));
  return NOTE_VIBE_COMPOSITIONS.find(profile=>profile.requires.every(vibe=>known.has(vibe)))?.label||null;
}

export function scentVibe(notes) {
  const facets=noteLedVibe(notes);
  return {facets,combined:composeNoteVibe(facets)};
}

const SCENT_ANALYSIS_CACHE=new WeakMap();
function analyzeScentRecord(fragrance) {
  const cached=SCENT_ANALYSIS_CACHE.get(fragrance);
  if(cached)return cached;
  const familyEvidenceByName=Object.fromEntries(FAMILIES.map(family=>[family,familyEvidence(family,fragrance)]));
  const vibeEvidence=noteLedVibe(fragrance.notes);
  const analysis={
    familyDataKnown:(fragrance.families||[]).length>0||Array.isArray(fragrance.notes),
    familyEvidenceByName,
    vibeEvidence,
    availableVibes:new Set(vibeEvidence.map(x=>x.vibe)),
    combinedVibe:composeNoteVibe(vibeEvidence),
  };
  SCENT_ANALYSIS_CACHE.set(fragrance,analysis);
  return analysis;
}

function climateMatch(wanted, available=[]) {
  if (!wanted) return {ratio:.5,label:'No climate preference'};
  if (!available.length) return {ratio:.5,label:'Climate suitability is unrecorded'};
  const ranked=available.map(value=>({value,distance:Math.abs(CLIMATE_ORDER.indexOf(value)-CLIMATE_ORDER.indexOf(wanted))})).filter(x=>x.distance>=0).sort((a,b)=>a.distance-b.distance);
  if (!ranked.length) return {ratio:.5,label:'Climate suitability is unrecorded'};
  const nearest=ranked[0];
  const ratio=[1,.7,.35,0][nearest.distance] ?? 0;
  const breezyFallback=wanted==='cold'&&nearest.value==='cool';
  const label=nearest.distance===0?`Fits your ${wanted} climate preference.`:breezyFallback
    ?'Closest climate tag is cool, your breezy fallback for cold; this is a nearby climate fit.'
    :`Closest climate tag is ${nearest.value} (you chose ${wanted}); this is a ${nearest.distance===1?'nearby':'looser'} climate fit.`;
  return {ratio,label};
}

function occasionMatch(wanted, available=[]) {
  if (!wanted) return {ratio:.5,label:'No occasion preference'};
  if (!available.length) return {ratio:.5,label:'Occasion suitability is unrecorded'};
  const nearest=available.map(value=>({value,ratio:OCCASION_NEARNESS[wanted]?.[value] ?? 0})).sort((a,b)=>b.ratio-a.ratio)[0];
  if (!nearest) return {ratio:.5,label:'Occasion suitability is unrecorded'};
  return {ratio:nearest.ratio,label:nearest.ratio===1?`Fits your ${wanted} occasion.`:`Closest occasion tag is ${nearest.value} (you chose ${wanted}); this is a ${nearest.ratio>=.7?'nearby':'looser'} occasion fit.`};
}

export function scoreFragrance(fragrance, answers) {
  const hasBudget=Number.isFinite(answers.budget);
  const ceiling=hasBudget?budgetLimit(answers):Infinity;
  const requestedGender=answers.gender;
  const genderEligible=!['male','female'].includes(requestedGender)||fragrance.gender===requestedGender||fragrance.gender==='unisex';
  // Wearer eligibility and price are hard gates. Scent, climate, occasion or
  // intensity preferences cannot bypass them.
  if (!genderEligible||(hasBudget&&(!Number.isFinite(fragrance.priceUsd)||fragrance.priceUsd<0||fragrance.priceUsd>ceiling)) || (Number.isFinite(fragrance.priceUsd)&&fragrance.priceUsd<0)) return null;

  const selected=[...new Set(answers.families||[])];
  const availableFamilies=fragrance.families||[];
  // An empty family list plus null notes means the scent profile is unknown,
  // not evidence that the fragrance misses every selected family.
  const scentAnalysis=analyzeScentRecord(fragrance);
  const familyDataKnown=scentAnalysis.familyDataKnown;
  const evidence=selected.map(f=>scentAnalysis.familyEvidenceByName[f]).filter(Boolean);
  const common=evidence.filter(e=>e.kind==='family').map(e=>e.family);
  const matched=evidence.map(e=>e.family);
  const missing=familyDataKnown?selected.filter(f=>!matched.includes(f)):[];
  const vibeEvidence=scentAnalysis.vibeEvidence;
  const availableVibes=scentAnalysis.availableVibes;
  const combinedVibe=scentAnalysis.combinedVibe;
  const vibeMatchedFamilies=selected.filter(f=>matched.includes(f)&&(FAMILY_VIBE_FACETS[f]||[]).some(vibe=>availableVibes.has(vibe)));
  const vibeScore=selected.length&&Array.isArray(fragrance.notes)?Math.min(1,vibeMatchedFamilies.length/selected.length+(combinedVibe?0.05:0)):null;
  // The user's scent-family requests can be matched by an explicit family tag
  // or by related notes; count each selected preference once.
  const familyRatio=selected.length?(familyDataKnown?evidence.length/selected.length:0):0.5;
  const climate=climateMatch(answers.weather,fragrance.climates||[]);
  const occasion=occasionMatch(answers.occasion,fragrance.occasions||[]);
  const intensityRatio=!answers.intensity?1:(fragrance.intensity == null ? 0.5 : fragrance.intensity===answers.intensity ? 1 : 0);
  const overBudget=hasBudget&&Number.isFinite(fragrance.priceUsd)&&fragrance.priceUsd>answers.budget;
  // The entered amount is the sweet spot, not a floor. Within the hard +20%
  // price limit, this component scores distance from target; recommendation
  // ordering uses that distance after selected family/note coverage.
  const budgetRatio=!hasBudget?0.5:answers.budget===0
    ? (fragrance.priceUsd===0?1:0)
    : Math.max(0,1-Math.abs(fragrance.priceUsd-answers.budget)/answers.budget);
  const parts={
    family:selected.length&&!familyDataKnown?null:WEIGHTS.family*familyRatio,
    weather:WEIGHTS.weather*climate.ratio,
    occasion:WEIGHTS.occasion*occasion.ratio,
    intensity:WEIGHTS.intensity*intensityRatio,
    budget:WEIGHTS.budget*budgetRatio,
  };
  const reasons=[];
  const noteEvidence=evidence.filter(e=>e.kind==='note');
  reasons.push(!selected.length
    ? 'No scent-family preference set.'
    : !familyDataKnown
      ? 'Family and key-note data are unavailable for this fragrance; its scent match is unverified.'
      : `Matches ${evidence.length} of ${selected.length} selected family or note preferences${missing.length?`; no listed match for ${missing.join(', ')}`:''}.`);
  if (common.length) reasons.push(`Explicit family tags: ${common.join(', ')}.`);
  if (noteEvidence.length) reasons.push(`Related note matches (not explicit family tags): ${noteEvidence.map(e=>`${e.family} through ${e.note}`).join(', ')}.`);
  if (combinedVibe) reasons.push(`Combined note profile: ${combinedVibe}. This is an editorial reading of the listed notes.`);
  if (vibeEvidence.length) reasons.push(`Note-led facets: ${vibeEvidence.slice(0,6).map(x=>`${x.vibe} (${x.notes.slice(0,2).join(', ')})`).join('; ')}.`);
  reasons.push(climate.label,occasion.label);
  if (answers.intensityFallback) reasons.push('No strong-intensity fragrance is recorded within the hard price limit, so moderate is used as the fallback preference.');
  if (answers.intensity) reasons.push(fragrance.intensity==null
    ? `Intensity is not verified; your ${answers.intensity} preference is treated as unknown, not a mismatch.`
    : fragrance.intensity===answers.intensity?`Matches your ${answers.intensity} intensity preference.`:`Intensity is tagged ${fragrance.intensity}; you chose ${answers.intensity}.`);
  const priceLabel=Number.isFinite(fragrance.priceUsd)?`${fragrance.priceStatus==='estimated'?'Estimated ':''}$${fragrance.priceUsd} / ${fragrance.priceReferenceSizeMl||fragrance.bottleSizeMl||100} ml`:'Price unavailable';
  if(hasBudget){
    const priceGap=Math.round(Math.abs(fragrance.priceUsd-answers.budget)*100)/100;
    const pricePosition=priceGap===0?'at your target':`${priceGap===Math.round(priceGap)?priceGap:priceGap.toFixed(2)} ${overBudget?'above':'below'} your target`;
    reasons.push(overBudget
      ? `${priceLabel} is ${pricePosition} and inside the firm $${ceiling} limit; price fit is ${parts.budget.toFixed(1)} of ${WEIGHTS.budget} points.`
      : `${priceLabel} is ${pricePosition}; price fit is ${parts.budget.toFixed(1)} of ${WEIGHTS.budget} points.`);
  }else reasons.push(`${priceLabel}; no budget preference is set, so price does not filter this fragrance.`);
  const extraFamilies=availableFamilies.filter(f=>!selected.includes(f));
  if (extraFamilies.length) reasons.push(`Other listed scent families to explore: ${extraFamilies.join(', ')}.`);

  const caveats=fragrance.dataCaveat?[fragrance.dataCaveat]:[];
  if (fragrance.priceStatus==='estimated') caveats.push(`Low-confidence 100 ml price estimate (about $${fragrance.priceEstimateRangeUsd?.[0]??fragrance.priceUsd}–$${fragrance.priceEstimateRangeUsd?.[1]??fragrance.priceUsd}); no exact retailer offer was verified. The price ceiling itself was not stretched.`);
  if (fragrance.notes==null) caveats.push('Key notes have not yet been source-verified.');
  if (selected.length&&!familyDataKnown) caveats.push('No family tags or key notes are recorded, so this fragrance cannot be confirmed against your scent preferences. Its fit score is normalized over recorded criteria and excludes the unverified family component.');
  if (answers.intensity&&fragrance.intensity==null) caveats.push(answers.intensityFallback?'Intensity is missing from this record; the moderate fallback cannot be verified for this fragrance.':'Intensity is missing from the catalog, so this preference could not be checked.');
  const rawScore=Object.values(parts).reduce((a,b)=>a+(b??0),0);
  const availablePoints=Object.entries(parts).reduce((sum,[key,value])=>sum+(value===null?0:WEIGHTS[key]),0);
  const score=availablePoints?Math.round(rawScore/availablePoints*1000)/10:0;
  return {fragrance,parts,overBudget,rawScore,availablePoints,score,reasons,caveats,missingFamilies:missing,matchedFamilies:matched,matchedFamilyCount:evidence.length,selectedFamilyCount:selected.length,familyDataKnown,vibeEvidence,combinedVibe,vibeScore};
}

export function recommend(catalog, answers, limit=RESULT_COUNT, {maxPerBrand=MAX_RECOMMENDATIONS_PER_BRAND}={}) {
  const ceiling=Number.isFinite(answers.budget)?budgetLimit(answers):Infinity;
  const priceEligible=catalog.filter(f=>(!['male','female'].includes(answers.gender)||f.gender===answers.gender||f.gender==='unisex')&&(!Number.isFinite(answers.budget)||(Number.isFinite(f.priceUsd)&&f.priceUsd>=0&&f.priceUsd<=ceiling)));
  const intensityFallback=answers.intensity==='strong'&&!priceEligible.some(f=>f.intensity==='strong');
  const rankedAnswers=intensityFallback?{...answers,intensity:'moderate',intensityFallback:true}:answers;
  const ranked=catalog.map(f=>scoreFragrance(f,rankedAnswers)).filter(Boolean)
    .sort((a,b)=>{
      // The budget cap is the first gate. Inside it, fulfill the selected
      // scent brief (3/3, then 2/3, then 1/3) before using price proximity.
      if(a.matchedFamilyCount!==b.matchedFamilyCount)return b.matchedFamilyCount-a.matchedFamilyCount;
      if(a.selectedFamilyCount>0&&a.familyDataKnown!==b.familyDataKnown)return Number(b.familyDataKnown)-Number(a.familyDataKnown);
      if(Number.isFinite(answers.budget)){
        const gapA=Number.isFinite(a.fragrance.priceUsd)?Math.abs(a.fragrance.priceUsd-answers.budget):Infinity;
        const gapB=Number.isFinite(b.fragrance.priceUsd)?Math.abs(b.fragrance.priceUsd-answers.budget):Infinity;
        if(gapA!==gapB)return gapA-gapB;
      }
      if(a.vibeScore!==null&&b.vibeScore!==null&&a.vibeScore!==b.vibeScore)return b.vibeScore-a.vibeScore;
      return b.rawScore-a.rawScore || Number(a.overBudget)-Number(b.overBudget) || a.fragrance.id.localeCompare(b.fragrance.id);
    });
  const resultLimit=Math.max(0,limit);
  if(resultLimit===0)return [];
  if(!Number.isFinite(maxPerBrand))return ranked.slice(0,resultLimit);
  const brandLimit=Math.max(0,Math.floor(maxPerBrand));
  const brandCounts=new Map();
  const diverse=[];
  for(const match of ranked){
    const brand=normalizeBrand(match.fragrance.brand||match.fragrance.id);
    const count=brandCounts.get(brand)||0;
    if(count>=brandLimit)continue;
    brandCounts.set(brand,count+1);
    diverse.push(match);
    if(diverse.length>=resultLimit)break;
  }
  return diverse;
}

export function filterCatalog(catalog,{query='',family='',families=[],gender='',weather='',occasion='',budget=null,includeUnknown=false,listedOnly=false,photosOnly=false,intensity=''}={}) {
  const ceiling=budget===null?Infinity:budgetLimit({budget});
  const q=query.trim().toLocaleLowerCase();
  const selected=[...new Set([...families,...(family?[family]:[])])];
  return catalog.filter(f=>(!photosOnly||(Boolean(f.image)&&f.imageProvider!=='Maison Sillage illustration'))&&(!listedOnly||f.priceStatus==='listed')&&(!q||`${f.brand} ${f.name} ${(f.notes||[]).join(' ')} ${(f.inspiredBy||[]).map(x=>`${x.brand||''} ${x.name||''}`).join(' ')}`.toLocaleLowerCase().includes(q))&&selected.every(v=>(f.families||[]).includes(v))&&(!gender||f.gender===gender||f.gender==='unisex')&&(!weather||(f.climates||[]).includes(weather))&&(!occasion||(f.occasions||[]).includes(occasion))&&(!intensity||f.intensity===intensity)&&(Number.isFinite(f.priceUsd)?f.priceUsd<=ceiling:budget===null||includeUnknown));
}

export function recommendationDiagnostics(catalog,answers) {
  const ceiling=budgetLimit(answers);
  const priceEligible=catalog.filter(f=>(!['male','female'].includes(answers.gender)||f.gender===answers.gender||f.gender==='unisex')&&Number.isFinite(f.priceUsd)&&f.priceUsd>=0&&f.priceUsd<=ceiling);
  const exactProfile=priceEligible.filter(f=>(answers.families||[]).every(x=>(f.families||[]).includes(x))&&(f.climates||[]).includes(answers.weather)&&(f.occasions||[]).includes(answers.occasion)&&(!answers.intensity||f.intensity===answers.intensity));
  return {
    ceiling,
    eligible:priceEligible.length,
    estimatedEligible:priceEligible.filter(f=>f.priceStatus==='estimated').length,
    exactEligible:exactProfile.length,
    unpriced:catalog.filter(f=>(!['male','female'].includes(answers.gender)||f.gender===answers.gender||f.gender==='unisex')&&!Number.isFinite(f.priceUsd)).length,
    aboveCeiling:catalog.filter(f=>(!['male','female'].includes(answers.gender)||f.gender===answers.gender||f.gender==='unisex')&&Number.isFinite(f.priceUsd)&&f.priceUsd>ceiling).length,
  };
}
