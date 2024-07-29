const { Menu, Transition } = HeadlessUIReact;
const { Fragment } = React;

function Dropdown({ label, items }) {
  return React.createElement(
    Menu,
    { as: "div", className: "relative inline-block text-left" },
    React.createElement(
      "div",
      null,
      React.createElement(
        Menu.Button,
        { className: "inline-flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-navy rounded-md hover:bg-raspberry focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75" },
        label
      )
    ),
    React.createElement(
      Transition,
      {
        as: Fragment,
        enter: "transition ease-out duration-100",
        enterFrom: "transform opacity-0 scale-95",
        enterTo: "transform opacity-100 scale-100",
        leave: "transition ease-in duration-75",
        leaveFrom: "transform opacity-100 scale-100",
        leaveTo: "transform opacity-0 scale-95"
      },
      React.createElement(
        Menu.Items,
        { className: "absolute right-0 w-56 mt-2 origin-top-right bg-white divide-y divide-gray-100 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" },
        React.createElement(
          "div",
          { className: "px-1 py-1" },
          items.map((item, index) => 
            React.createElement(
              Menu.Item,
              { key: index },
              ({ active }) => React.createElement(
                "button",
                { 
                  className: `${active ? 'bg-light-blue text-white' : 'text-gray-900'} group flex rounded-md items-center w-full px-2 py-2 text-sm`
                },
                item
              )
            )
          )
        )
      )
    )
  );
}