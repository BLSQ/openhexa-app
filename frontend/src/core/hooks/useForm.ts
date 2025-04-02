import isEqual from "lodash/isEqual";
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
  [key: string]: string;
};

export type FormInstance<T, TData = void> = {
  formData: Partial<T>;
  submitError: string | null;
  previousFormData: Partial<T> | undefined;
  errors: { [key in keyof T]?: FormFieldError };
  handleInputChange: ChangeEventHandler<
    HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
  >;
  setDebouncedFieldValue: (
    fieldName: keyof T,
    value: any,
    delay?: number,
  ) => void;
  setFieldValue: (fieldName: keyof T, value: any, isTouched?: boolean) => void;
  setFormData: (formData: Partial<T>) => void;
  resetForm: () => void;
  validate(): void;
  handleSubmit(event?: {
    preventDefault: Function;
    stopPropagation: Function;
  }): Promise<TData | void> | TData | void;
  touched: { [key in keyof Partial<T>]: boolean };
  isDirty: boolean;
  isSubmitting: boolean;
};

type FormFieldError = string;

type UseFormOptions<T> = {
  initialState?: Partial<T>;
  getInitialState?: () => Partial<T>;
  onSubmit: (formData: T) => void | Promise<any>;
  validate?: (values: Partial<T> & { [key: string]: any }) => {
    [key in keyof T]: FormFieldError;
  };
};

function useForm<T = FormData, TData = void>(
  options: UseFormOptions<T>,
): FormInstance<T, TData> {
  const { t } = useTranslation();
  const { initialState = {}, getInitialState, validate, onSubmit } = options;
  const [isSubmitting, setSubmitting] = useState(false);
  const errorsRef = useRef<{ [key in keyof T]?: FormFieldError }>({});
  const timeouts = useRef<{ [key in keyof T]?: any }>({});
  const [hasBeenSubmitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [touched, setTouched] = useState<
    | {
        [key in keyof Partial<T>]: boolean;
      }
    | {}
  >({});

  // Validate on submit

  // This is intended to always return the same object to avoid to have side-effect in useEffect because of a object ref change
  const uniqueRef = useRef<{}>({});
  const internalInitialState = useRef<Partial<T>>();

  const setInitialState = useCallback(() => {
    if (getInitialState) {
      internalInitialState.current = getInitialState() as T;
    } else {
      internalInitialState.current = initialState ?? {};
    }
  }, [internalInitialState, getInitialState, initialState]);
  if (!internalInitialState.current) {
    setInitialState();
  }
  const [formData, setFormData] = useState<Partial<T>>(
    internalInitialState.current ?? {},
  );
  const previousFormData = usePrevious<Partial<T>>(formData);

  const _validate = useCallback(() => {
    if (!validate) {
      errorsRef.current = {};
    } else {
      errorsRef.current = validate(formData) ?? {};
    }

    return Object.values(errorsRef.current).filter(Boolean).length === 0;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData]);

  // useEffect(() => _validate(), [_validate]);

  const resetForm = useCallback(() => {
    setSubmitted(false);
    Object.values(timeouts).forEach((timeout) => clearTimeout(timeout));
    timeouts.current = {};
    setTouched({});
    errorsRef.current = {};
    setSubmitError(null);
    setInitialState();
    setFormData(internalInitialState.current ?? {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setInitialState]);

  const handleInputChange: ChangeEventHandler<
    HTMLInputElement | HTMLSelectElement
  > = useCallback(
    (event) => {
      if (
        event.target instanceof HTMLInputElement &&
        event.target.type === "checkbox"
      ) {
        setFieldValue(event.target.name as keyof T, event.target.checked);
      } else {
        setFieldValue(event.target.name as keyof T, event.target.value);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const setFieldValue = useCallback(
    (field: keyof T, value: any, isTouched = true) => {
      setFormData((formData) => ({
        ...formData,
        [field]: value,
      }));
      setTouched((touched) => ({
        ...touched,
        [field]: isTouched,
      }));
    },
    [],
  );

  const setDebouncedFieldValue = useCallback(
    (field: keyof T, value: any, delay: number = 200) => {
      clearTimeout(timeouts.current[field]);
      timeouts.current = {
        ...timeouts.current,
        [field]: setTimeout(() => {
          delete timeouts.current[field];
          timeouts.current = {
            ...timeouts.current,
          };
          setFieldValue(field, value);
        }, delay),
      };
    },
    [setFieldValue],
  );

  const handleSubmit = useCallback(
    async (event?: { preventDefault: Function; stopPropagation: Function }) => {
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }

      if (isSubmitting) return;

      setSubmitError(null);
      setSubmitting(true);
      setSubmitted(true);

      if (_validate() && Object.keys(timeouts.current).length === 0) {
        try {
          const result = await onSubmit(formData as T);
          setInitialState();
          return result;
        } catch (err: any) {
          setSubmitError(
            err.message ?? (t("An unexpected error occurred.") as string),
          );
        } finally {
          setSubmitting(false);
        }
      }
      setSubmitting(false);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [formData, touched],
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
    () => !isEqual(formData, internalInitialState.current),
    [formData, internalInitialState],
  );

  const result = useMemo(
    () =>
      Object.assign(uniqueRef.current, {
        formData,
        previousFormData,
        errors: errorsRef.current,
        submitError,
        isDirty,
        touched: allTouched,
        handleInputChange,
        setFieldValue,
        setDebouncedFieldValue,
        setFormData,
        validate: _validate,
        resetForm,
        isSubmitting,
        handleSubmit,
      }),
    [
      formData,
      previousFormData,
      errorsRef,
      submitError,
      isDirty,
      allTouched,
      handleInputChange,
      setFieldValue,
      setFormData,
      setDebouncedFieldValue,
      resetForm,

      isSubmitting,
      handleSubmit,
      _validate,
    ],
  );
  return result;
}

export default useForm;
