export default function (config) {
  config.ignores.add('src/evidence/**');
  config.addPassthroughCopy({'src/assets':'assets','src/evidence':'evidence','src/_headers':'_headers','src/_redirects':'_redirects'});
  config.addFilter('pad2', value => String(value).padStart(2,'0'));
  config.addFilter('dateLabel', date => new Intl.DateTimeFormat('en-US',{month:'long',day:'numeric',year:'numeric',timeZone:'UTC'}).format(new Date(date)));
  config.addFilter('rssDate', date => new Date(date).toUTCString());
  config.addFilter('isoDate', date => new Date(date).toISOString());
  config.addFilter('searchText', text => String(text).replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim());
  config.addFilter('absolute', path => new URL(path,'https://mayos.dev').href);
  config.addFilter('json', data => JSON.stringify(data));
  config.addCollection('posts', api => api.getFilteredByTag('post').sort((a,b)=>b.date-a.date));
  config.addCollection('topics', api => [...new Set(api.getFilteredByTag('post').flatMap(post=>post.data.topics||[]))].sort());
  return {dir:{input:'src',includes:'_includes',data:'_data',output:'_site'},markdownTemplateEngine:'njk',htmlTemplateEngine:'njk'};
}
