// Load links from local storage or initialize an empty array
let links = JSON.parse(localStorage.getItem('links')) || [];

// Add your referral links below
links.push({
  name: 'Camp',
  url: 'https://www.eventbrite.com/e/faith-check-2023-tickets-632837683547',
  description: "We're going to camp fr fr"
});

links.push({
  name: 'Link 2',
  url: 'https://www.example.com/referral2',
  description: 'Description for Link 2'
});

// Function to render the link list
function renderLinks() {
  const linkList = document.getElementById('link-list');
  linkList.innerHTML = '';

  links.forEach(function (link) {
    const linkItem = document.createElement('div');
    linkItem.classList.add('link-item');

    const heading = document.createElement('h2');
    heading.textContent = link.name;
    linkItem.appendChild(heading);

    const content = document.createElement('div');
    content.classList.add('link-content');

    const linkAnchor = document.createElement('a');
    linkAnchor.href = link.url;
    linkAnchor.textContent = 'Link';
    content.appendChild(linkAnchor);

    const description = document.createElement('p');
    description.textContent = link.description;
    content.appendChild(description);

    linkItem.appendChild(content);
    linkList.appendChild(linkItem);

    // Add event listener to toggle the content visibility
    heading.addEventListener('click', function () {
      content.classList.toggle('show');
    });
  });
}

// Call the renderLinks function initially
renderLinks();
