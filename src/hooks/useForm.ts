import _ from "lodash";
import { useTranslation } from "next-i18next";
import {
  ChangeEventHandler,
  useCallback,
  useMemo,
  useRef,
  useState,
} from "react";
import usePrevious from "./usePrevious";

type FormData = {
  string?: string;
};

type UseFormResult<T> = {
  formData: Partial<T>;
  submitError: string | null;
  previousFormData: Partial<T> | undefined;
  errors: { [key in keyof T]?: FormFieldError };
  handleInputChange: ChangeEventHandler<HTMLInputElement>;
  setFieldValue: (fieldName: string, value: any, isTouched?: boolean) => void;
  resetForm: () => void;
  handleSubmit: (event?: { preventDefault: Function }) => Promise<void> | void;
  touched: { [key in keyof Partial<T>]: boolean };
  isValid: boolean;
  isDirty: boolean;
  isSubmitting: boolean;
};

type FormFieldError = string;

type UseFormOptions<T> = {
  initialState?: Partial<T>;
  getInitialState?: () => Partial<T>;
  onSubmit: (formData: T) => void | Promise<any>;
  validate?: (values: Partial<T>) => {
    [key in keyof T]: FormFieldError;
  };
};

function useForm<T = FormData>(options: UseFormOptions<T>): UseFormResult<T> {
  const { t } = useTranslation();
  const { initialState = {}, getInitialState, validate, onSubmit } = options;
  const [touched, setTouched] = useState<
    | {
        [key in keyof Partial<T>]: boolean;
      }
    | {}
  >({});

  const internalInitialState = useRef<Partial<T>>({});

  const setInitialState = () => {
    internalInitialState.current = (
      getInitialState ? getInitialState() : initialState
    ) as T;
  };
  if (!internalInitialState.current) {
    setInitialState();
  }
  const [isSubmitting, setSubmitting] = useState(false);
  const [hasBeenSubmitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<T>>(
    internalInitialState.current
  );
  const previousFormData = usePrevious<Partial<T>>(formData);

  const resetForm = useCallback(() => {
    setSubmitted(false);
    setTouched({});
    setSubmitError(null);
    setInitialState();
    setFormData(internalInitialState.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [getInitialState, initialState]);

  const handleInputChange: ChangeEventHandler<HTMLInputElement> = useCallback(
    (event) => {
      if (event.target.type === "checkbox") {
        setFieldValue(event.target.name, event.target.checked);
      } else {
        setFieldValue(event.target.name, event.target.value);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const setFieldValue = useCallback(
    (field: string, value: any, isTouched = true) => {
      setFormData((formData) => ({
        ...formData,
        [field]: value,
      }));
      setTouched((touched) => ({
        ...touched,
        [field]: isTouched,
      }));
    },
    []
  );

  const errors = useMemo(() => {
    if (!validate) {
      return {};
    }

    const errors = validate(formData);
    return errors || {};
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData]);

  const isValid = useMemo(
    () => Object.values(errors).filter(Boolean).length === 0, // Ignore {myField: null | undefined}
    [errors]
  );

  const handleSubmit = useCallback(
    async (event?: { preventDefault: Function }) => {
      event?.preventDefault();
      if (isSubmitting) return;

      setSubmitError(null);
      setSubmitting(true);
      setSubmitted(true);

      if (isValid) {
        try {
          await onSubmit(formData as T);
          setInitialState();
        } catch (err: any) {
          setSubmitError(
            err.message ?? (t("An unexpected error ocurred.") as string)
          );
        } finally {
          setSubmitting(false);
        }
      }
      setSubmitting(false);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [formData, errors, isValid, touched]
  );

  // Proxy the touched fields to ensure that all errors are shown when the user ...
  // ... has already tried to submit the form.
  const allTouched = useMemo(() => {
    return new Proxy(touched, {
      get(target: any, prop: string) {
        return hasBeenSubmitted || target[prop];
      },
    });
  }, [touched, hasBeenSubmitted]);

  const isDirty = useMemo(
    () => !_.isEqual(formData, internalInitialState.current),
    [formData, internalInitialState]
  );

  return {
    formData,
    previousFormData,
    errors,
    submitError,
    isDirty,
    touched: allTouched,
    handleInputChange,
    setFieldValue,
    resetForm,
    isValid,
    isSubmitting,
    handleSubmit,
  };
}

export default useForm;
