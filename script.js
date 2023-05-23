let links = [
  {
    name: 'Link 1',
    url: 'https://www.example.com/referral1',
    description: 'Description for Link 1',
    category: 'Finances'
  },
  {
    name: 'Link 2',
    url: 'https://www.example.com/referral2',
    description: 'Description for Link 2',
    category: 'Games'
  },
  {
    name: 'Link 3',
    url: 'https://www.example.com/referral3',
    description: 'Description for Link 3',
    category: 'Services'
  },
  {
    name: 'Link 4',
    url: 'https://www.example.com/referral4',
    description: 'Description for Link 4',
    category: 'Others'
  }
];

function renderLinks() {
  // Clear existing content
  document.getElementById('link-list').innerHTML = '';

  // Create columns
  const categories = ['Finances', 'Games', 'Services', 'Others'];
  categories.forEach(category => {
    const columnDiv = document.createElement('div');
    columnDiv.classList.add('column');

    const columnHeading = document.createElement('h3');
    columnHeading.textContent = category;
    columnDiv.appendChild(columnHeading);

    // Filter links by category
    const filteredLinks = links.filter(link => link.category === category);

    // Create links for the current category
    filteredLinks.forEach(link => {
      const linkItem = document.createElement('div');
      linkItem.classList.add('link-item');

      const linkHeading = document.createElement('h2');
      linkHeading.textContent = link.name;
      linkItem.appendChild(linkHeading);

      const linkContent = document.createElement('div');
      linkContent.classList.add('link-content');

      const linkURL = document.createElement('a');
      linkURL.href = link.url;
      linkURL.textContent = 'Go to link';
      linkContent.appendChild(linkURL);

      const linkDescription = document.createElement('p');
      linkDescription.textContent = link.description;
      linkContent.appendChild(linkDescription);

      linkItem.appendChild(linkContent);
      columnDiv.appendChild(linkItem);
    });

    // Append the column to the main link-list element
    document.getElementById('link-list').appendChild(columnDiv);
  });
}

renderLinks();
