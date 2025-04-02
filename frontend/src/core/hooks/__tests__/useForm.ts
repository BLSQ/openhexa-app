import { renderHook, waitFor } from "@testing-library/react";
import useForm from "../useForm";

describe("useForm", () => {
  const onSubmit = jest.fn();
  const onValidate = jest.fn().mockReturnValue({});
  const FAKE_EVENT = {
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
  };

  afterEach(() => {
    onSubmit.mockClear();
    onValidate.mockClear();
    FAKE_EVENT.preventDefault.mockClear(),
      FAKE_EVENT.stopPropagation.mockClear();
  });

  it("mounts", async () => {
    const { result } = renderHook(() =>
      useForm<any>({
        onSubmit,
        validate: onValidate,
        initialState: {
          field1: "default_value",
        },
      }),
    );

    expect(onSubmit).not.toHaveBeenCalled();
    expect(onValidate).not.toHaveBeenCalled();
  });

  it("calls validate on submit", async () => {
    const { result } = renderHook(() =>
      useForm<any>({
        onSubmit,
        validate: onValidate,
        initialState: {
          field1: "default_value",
        },
      }),
    );

    await waitFor(() => {
      result.current.setFieldValue("field1", "new_value");
    });

    await waitFor(() => {
      expect(onValidate).not.toHaveBeenCalled();
    });
    await waitFor(async () => {
      await result.current.handleSubmit(FAKE_EVENT);
      expect(onSubmit).toHaveBeenCalledWith({ field1: "new_value" });
    });

    await waitFor(() => {
      expect(FAKE_EVENT.preventDefault).toHaveBeenCalled();
      expect(FAKE_EVENT.stopPropagation).toHaveBeenCalled();
    });
  });

  it("should reset the form", async () => {
    const { result } = renderHook(() =>
      useForm<any>({
        onSubmit,
        validate: onValidate,
        initialState: {
          field1: "default_value",
        },
      }),
    );
    await waitFor(() => {
      result.current.setFieldValue("field2", "value_2");
      result.current.setFieldValue("field1", "value_1");
      result.current.resetForm();
    });

    await waitFor(() => {
      result.current.handleSubmit();
    });

    expect(onSubmit).toHaveBeenCalledWith({ field1: "default_value" });
  });

  it("should call the getInitialState on reset", async () => {
    const getInitialState = jest
      .fn()
      .mockReturnValue({ field1: "default_value" });
    const { result } = renderHook(() =>
      useForm<any>({
        onSubmit,
        validate: onValidate,
        getInitialState,
      }),
    );

    expect(getInitialState).toHaveBeenCalled();

    getInitialState.mockClear();

    await waitFor(() => {
      result.current.resetForm();
      expect(getInitialState).toHaveBeenCalled();
    });
  });

  it("should mark the changed fields as touched", async () => {
    const { result } = renderHook(() =>
      useForm<any>({
        onSubmit,
        validate: onValidate,
        initialState: {
          field1: "value_1",
          field2: "value_2",
        },
      }),
    );

    expect(result.current.touched).toEqual({});
    expect(result.current.isDirty).toBe(false);

    await waitFor(() => {
      result.current.setFieldValue("field1", "new_value_1");
    });

    await waitFor(() => {
      expect(result.current.touched).toEqual({ field1: true });
      expect(result.current.isDirty).toBe(true);
    });
  });

  it("should validates the form values", async () => {
    onValidate.mockImplementation((values) => {
      if (values.field1 !== "good_value_1") {
        return { field1: "Wrong" };
      }
      return {};
    });
    const { result } = renderHook(() =>
      useForm<any>({
        onSubmit,
        validate: onValidate,
        initialState: {
          field1: "value_1",
          field2: "value_2",
        },
      }),
    );
    await result.current.handleSubmit();
    await waitFor(() => {
      expect(result.current.errors).toEqual({ field1: "Wrong" });
      expect(onSubmit).not.toHaveBeenCalled();
    });
    await waitFor(() => {
      result.current.setFieldValue("field1", "good_value_1");
    });
    await result.current.handleSubmit();

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalled();
    });
  });
});
