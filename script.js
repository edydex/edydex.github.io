// Load links from local storage or initialize an empty array
let links = JSON.parse(localStorage.getItem('links')) || [];

// Function to render the link list
function renderLinks() {
  const linkList = document.getElementById('link-list');
  linkList.innerHTML = '';

  links.forEach(function (link) {
    const listItem = document.createElement('li');
    listItem.innerHTML = `<a href="${link.url}">${link.name}</a>`;
    linkList.appendChild(listItem);
  });
}

// Function to handle the form submission
function handleSubmit(event) {
  event.preventDefault();
  const nameInput = document.getElementById('link-name');
  const urlInput = document.getElementById('link-url
