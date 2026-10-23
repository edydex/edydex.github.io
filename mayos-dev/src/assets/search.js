(() => {
  const input = document.querySelector('#post-search');
  if (!input) return;
  const posts = [...document.querySelectorAll('[data-post]')];
  const clear = document.querySelector('#clear-search');
  const status = document.querySelector('#search-status');
  const empty = document.querySelector('#no-results');
  const normalize = value => value.normalize('NFKD').replace(/\p{M}/gu, '').toLocaleLowerCase();
  const index = posts.map(post => ({post, text: normalize(post.dataset.search)}));
  const filter = () => {
    const terms = normalize(input.value).trim().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const {post, text} of index) {
      post.hidden = !terms.every(term => text.includes(term));
      if (!post.hidden) count++;
    }
    clear.hidden = !input.value;
    empty.hidden = count !== 0;
    status.textContent = `${count} ${count === 1 ? 'note' : 'notes'}${terms.length ? ' found' : ''}`;
    const url = new URL(location.href);
    if (input.value.trim()) url.searchParams.set('q', input.value.trim());
    else url.searchParams.delete('q');
    history.replaceState(null, '', url);
  };
  input.value = new URLSearchParams(location.search).get('q') || '';
  input.addEventListener('input', filter);
  clear.addEventListener('click', () => {input.value = ''; filter(); input.focus();});
  document.querySelector('[data-search-controls]').hidden = false;
  filter();
})();
