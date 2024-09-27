export default function PathWithError() {
  const triggerError = () => {
    throw new Error("This is an error");
  };
  return (
    <div>
      <h1>PathWithError</h1>
      <button onClick={triggerError}>Click me</button>
    </div>
  );
}
