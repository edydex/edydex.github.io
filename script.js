let links = [
  {
    name: 'Cash App',
    url: 'https://f5kbvc75.r.us-west-2.awstrack.me/L0/https:%2F%2Fcash.app%2Fdownload/1/010101884aacdccb-30cd9258-3fdd-4cb8-b0b1-b94dd4c016bc-000000/L25gBJWWPWo-hmk7mMZSb-ZboZ8=324',
    description: 'Enter the code "DGMTXVG" when you sign up and we both will get $5',
    category: 'Finances'
  },
  {
    name: 'Venmo',
    url: 'https://get.venmo.com/ayBXLT9V2zb',
    description: 'Use code "ayBXLT9V2zb" to get $10 after you send at least $5 to another person using Venmo. Can be added even after you created your account. If you are looking for someone to send money to - send it to me - @edydex :)',
    category: 'Finances'
  },
  {
    name: 'BitSkins',
    url: 'bskn.co/?ref_alias=5SA78YdnDi4',
    description: 'Use code "5SA78YdnDi4", I earn 1% from your purchases. You can also see my for-sale inventory at https://bskn.co/inventory?alias=5SA78YdnDi4&app_id=730 ',
    category: 'Games'
  },
  {
    name: 'Link 3',
    url: 'https://www.example.com/referral3',
    description: 'Description for Link 3',
    category: 'Services'
  },
  {
    name: 'D-Market',
    url: 'https://dmarket.com?ref=QEwdU8FHZo',
    description: 'Buy and Sell CS2 skins. I get 0.5-1% from the things you sell or buy. ',
    category: 'Games'
  },
  {
    name: 'Placeholder',
    url: 'https://www.example.com/referral3',
    description: 'Description for Link 3',
    category: 'Others'
  },
  // Add more links here using the same structure
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

      // Add event listener to toggle link content visibility
      linkHeading.addEventListener('click', () => {
        linkContent.classList.toggle('show');
      });
    });

    // Append the column to the main link-list element
    document.getElementById('link-list').appendChild(columnDiv);
  });
}

renderLinks();
