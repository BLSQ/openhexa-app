const Comments = () => {
  const user = {
    name: "Whitney Francis",
    email: "whitney@example.com",
    imageUrl:
      "https://images.unsplash.com/photo-1517365830460-955ce3ccd263?ixlib=rb-=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=8&w=256&h=256&q=80",
  };
  const comments = [
    {
      id: 1,
      name: "Leslie Alexander",
      date: "4d ago",
      imageId: "1494790108377-be9c29b29330",
      body: "Ducimus quas delectus ad maxime totam doloribus reiciendis ex. Tempore dolorem maiores. Similique voluptatibus tempore non ut.",
    },
    {
      id: 2,
      name: "Michael Foster",
      date: "4d ago",
      imageId: "1519244703995-f4e0f30006d5",
      body: "Et ut autem. Voluptatem eum dolores sint necessitatibus quos?",
    },
  ];

  return (
    <div className="-mx-4 -my-5 sm:-mx-6">
      <div className="divide-y divide-gray-200">
        <div className="px-4 py-6 sm:px-6">
          <ul role="list" className="max-w-4xl space-y-8">
            {comments.map((comment) => (
              <li key={comment.id}>
                <div className="flex space-x-3">
                  <div className="shrink-0">
                    <img
                      className="h-10 w-10 rounded-full"
                      src={`https://images.unsplash.com/photo-${comment.imageId}?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80`}
                      alt=""
                    />
                  </div>
                  <div>
                    <div className="text-sm">
                      <a href="#" className="font-medium text-gray-900">
                        {comment.name}
                      </a>
                    </div>
                    <div className="mt-1 text-sm text-gray-700">
                      <p>{comment.body}</p>
                    </div>
                    <div className="mt-2 space-x-2 text-sm">
                      <span className="font-medium text-gray-500">
                        {comment.date}
                      </span>{" "}
                      <span className="font-medium text-gray-500">
                        &middot;
                      </span>{" "}
                      <button
                        type="button"
                        className="font-medium text-gray-900"
                      >
                        Reply
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="bg-gray-50 px-4 py-6 sm:px-6">
        <div className="flex space-x-3">
          <div className="shrink-0">
            <img
              className="h-10 w-10 rounded-full"
              src={user.imageUrl}
              alt=""
            />
          </div>
          <div className="min-w-0 max-w-4xl flex-1 ">
            <form action="#">
              <div>
                <label htmlFor="comment" className="sr-only">
                  About
                </label>
                <textarea
                  id="comment"
                  name="comment"
                  rows={3}
                  className="form-textarea block w-full rounded-md border border-gray-300 shadow-xs focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  placeholder="Add a note"
                  defaultValue={""}
                />
              </div>
              <div className="mt-3 flex items-center justify-start">
                <button
                  type="submit"
                  className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-xs hover:bg-blue-700 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Comment
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Comments;
