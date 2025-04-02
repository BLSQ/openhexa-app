import DataCard from "../DataCard";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { faker } from "@faker-js/faker";
import TextProperty from "../TextProperty";

function nextFrame() {
  return new Promise<void>((resolve) => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        resolve();
      });
    });
  });
}

describe("DataCard", () => {
  it("renders", async () => {
    const item = {
      name: faker.person.jobDescriptor(),
    };
    const { container } = render(
      <DataCard item={item}>
        <DataCard.Heading titleAccessor="name" />
        <DataCard.FormSection>
          <TextProperty id="name" label="Name" accessor="name" />
        </DataCard.FormSection>
      </DataCard>,
    );

    expect(container).toMatchSnapshot();
  });
});
