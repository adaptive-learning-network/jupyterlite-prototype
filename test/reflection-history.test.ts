import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mergeReflections } from '../src/extension/reflection-history';
import { reflectionText } from '../src/extension/reflection-export';
import { ReflectionEntry } from '../src/engine';

test('wording updates keep stable answers, original prompt and earlier writing', () => {
 const old: ReflectionEntry[] = [{id:'q1',version:1,prompt:'Old wording?',answer:'My original answer',savedAt:'2026-10-21T12:00:00Z'}];
 const before = JSON.stringify(old);
 const updated = mergeReflections(old, [{id:'q1',version:1,prompt:'Clearer wording?',answer:'My revised answer'}], '2026-10-22T12:00:00Z');
 assert.equal(updated.length,1);
 assert.equal(updated[0].answer,'My revised answer');
 assert.deepEqual(updated[0].history,[{prompt:'Old wording?',answer:'My original answer',savedAt:'2026-10-21T12:00:00Z'}]);
 assert.equal(JSON.stringify(old),before);
});
test('changed meaning and removed questions retain separate answers and download history', () => {
 const old: ReflectionEntry[] = [{id:'q1',version:1,prompt:'Original question?',answer:'Original answer',savedAt:'before'},
  {prompt:'Removed legacy question?',answer:'Keep this too',savedAt:'before'}];
 const updated = mergeReflections(old, [{id:'q1',version:2,prompt:'Different question?',answer:'New answer'}], 'after');
 assert.equal(updated.length,3);
 assert.equal(updated[0].answer,'Original answer');
 const cleared = mergeReflections(updated,[{id:'q1',version:2,prompt:'Different question?',answer:''}],'later');
 assert.equal(cleared[2].answer,'');
 assert.equal(cleared[2].history![0].answer,'New answer');
 const text=reflectionText({schema:'al-learner-record/0.1',learner:'test',audience:'test',observations:[],guidance:{},reflections:{test:cleared}});
 for(const value of ['Original answer','Keep this too','New answer','Earlier recorded response']) assert.ok(text.includes(value));
});
test('legacy matching is exact and preserves unrelated records', () => {
 const old=[{prompt:'Original wording?',answer:'Legacy answer',savedAt:'before'}, {prompt:'Other?',answer:'Other answer',savedAt:'before'}];
 const updated=mergeReflections(old,[{id:'q1',version:1,prompt:'New wording?',legacyPrompts:['Original wording?'],answer:'Legacy answer'}],'after');
 assert.equal(updated.length,2);assert.equal(updated[0].id,'q1');assert.equal(updated[1].answer,'Other answer');
 assert.equal(updated[0].history![0].prompt,'Original wording?');
});

test('a new meaning does not automatically migrate an unversioned legacy answer', () => {
 const old=[{prompt:'Same short wording?',answer:'Legacy meaning',savedAt:'before'}];
 const updated=mergeReflections(old,[{id:'q1',version:2,prompt:'Same short wording?',legacyPrompts:['Same short wording?'],answer:'Revised meaning'}],'after');
 assert.equal(updated.length,2);assert.equal(updated[0].answer,'Legacy meaning');
});
