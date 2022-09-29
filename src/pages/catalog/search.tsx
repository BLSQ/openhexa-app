import DatasourcePicker from "catalog/features/DatasourcePicker";
import SearchInput from "catalog/features/SearchInput";
import SearchResult from "catalog/features/SearchResult";
import useSearch, { UseSearchOptions } from "catalog/hooks/useSearch";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Field from "core/components/forms/Field";
import Select from "core/components/forms/Select";
import { PageContent } from "core/components/Layout/PageContent";
import { createGetServerSideProps } from "core/helpers/page";
import useForm from "core/hooks/useForm";
import { useTranslation } from "next-i18next";
import { useState } from "react";

type SearchForm = {
  query: string;
  datasources: { id: string; label: string }[] | null;
  types: { id: string; label: string }[] | null;
};

const SearchPage = () => {
  const { t } = useTranslation();
  const [searchOptions, setSearchOptions] = useState<UseSearchOptions>({});

  const form = useForm<SearchForm>({
    initialState: {
      query: "",
      datasources: [],
      types: null,
    },
    onSubmit(values) {
      console.log(values);
      setSearchOptions({
        query: values.query,
        datasourceIds: values.datasources?.map((d) => d.id),
        types: values.types?.map((t) => t.id),
        perPage: 50,
      });
    },
  });

  const { results, types, loading } = useSearch(searchOptions);

  return (
    <PageContent>
      <Breadcrumbs className="my-8 px-2">
        <Breadcrumbs.Part href="/catalog">{t("Catalog")}</Breadcrumbs.Part>
        <Breadcrumbs.Part href="/catalog/search">
          {t("Search")}
        </Breadcrumbs.Part>
      </Breadcrumbs>
      <div className="space-y-4">
        <Block className="">
          <Block.Content className="border-b  border-b-gray-200 bg-gray-50">
            <form onSubmit={form.handleSubmit} className="space-y-4">
              <SearchInput
                value={form.formData.query}
                loading={loading}
                required
                className="flex-1 rounded-md border border-gray-300 bg-white px-4 py-1"
                name="query"
                onChange={form.handleInputChange}
              />
              <div className="mt-1 text-sm text-gray-500">
                {t(
                  'Enter one or more search terms separated by spaces. Use "quotes" for exact matches.'
                )}
              </div>
              <h4 className="text-sm font-medium">{t("Additional Filters")}</h4>
              <div className="grid grid-cols-5 gap-4">
                <Field
                  name="datasources"
                  label={t("By source")}
                  required
                  className="col-span-2"
                >
                  <DatasourcePicker
                    multiple
                    placeholder="Datasource"
                    value={form.formData.datasources}
                    onChange={(values) =>
                      form.setFieldValue("datasources", values)
                    }
                    name="datasources"
                  />
                </Field>
                <Field
                  className="col-span-2"
                  label={t("By type")}
                  name="types"
                  required
                >
                  <Select
                    placeholder="Type"
                    multiple
                    value={form.formData.types ?? null}
                    onChange={(types) => form.setFieldValue("types", types)}
                    options={
                      types?.map((t) => ({ id: t.value, label: t.label })) ?? []
                    }
                  />
                </Field>
              </div>
              <div className="text-right">
                <Button type="submit">{t("Search")}</Button>
              </div>
            </form>
          </Block.Content>

          <div id="results">
            {results?.length === 0 && searchOptions.query && (
              <div className="p-4 text-sm text-gray-500">
                {t("No results to display.")}
              </div>
            )}

            {results && results.length !== 0 && (
              <div className="divide-y divide-gray-100 overflow-y-auto ">
                {results.map((result) => (
                  <div className="h-20" key={result.object.id}>
                    <SearchResult className="h-full px-6" result={result} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </Block>
      </div>
    </PageContent>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default SearchPage;
