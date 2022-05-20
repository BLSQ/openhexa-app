const SAMPLE_DESCRIPTION = `
### At vero eos
Accusamus *et iusto odio dignissimos ducimus qui blanditiis* praesentium voluptatum deleniti atque 
corrupti _quos dolores_ et \`quas molestias\` excepturi sint occaecati cupiditate non provident, similique sunt 
in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga.
Et harum quidem rerum facilis est et expedita distinctio.
      
> nihil impedit quo minus id quod maxime placeat facere possimus.

1. Nam libero tempore
2. Cum soluta nobis est eligendi optio [cumque](https://bluesquare.org) 

**Omnis voluptas assumenda** est, omnis dolor repellendus.Temporibus autem.

Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. 
Phasellus laoreet tincidunt ligula, ac semper nisi placerat ut. Mauris congue, velit sed aliquam feugiat, ipsum 
mi maximus dui, non maximus odio libero sed dolor.

Sed luctus tellus et ipsum mollis uisque ac viverra libero, vitae [hendrerit quam](https://www.bluesquarehub.com).
`;

export const FAKE_COLLECTIONS = [
  {
    id: "1",
    name: "Democratic Republic of Congo C19",
    location: "COD",
    locationCode: "cd",
    createdBy: "Grégoire Lurton",
    visibility: "Shared",
    createdAt: "April 17, 2022",
    excerpt:
      "Data sources, notebooks and dashboard for Covid-19 monitoring in the Democratic Republic of Congo",

    description: SAMPLE_DESCRIPTION,
    tags: ["Covid-19", "Malaria", "Vaccination"],
  },
  {
    id: "2",
    name: "Burkina Faso Malaria vaccination",
    location: "BFA",
    locationCode: "bf",
    createdBy: "Alex Kaldjian",
    visibility: "Public",
    createdAt: "April 14, 2022",
    excerpt:
      "Malaria-related data from Burkina Faso, focused on the ongoing vaccination efforts",
    description: SAMPLE_DESCRIPTION,
    tags: ["Malaria", "Vaccination"],
  },
  {
    id: "3",
    name: "IHP working data",
    createdBy: "Fernando Valdés-Bango",
    location: "COD",
    locationCode: "cd",
    visibility: "Private",
    createdAt: "April 11, 2022",
    description: SAMPLE_DESCRIPTION,
    tags: [],
  },
];
