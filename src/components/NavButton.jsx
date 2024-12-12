const NavButton = ({ icon, label, onClick, active }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center space-y-1 ${active ? 'text-blue-600' : 'text-gray-700'}`}
  >
    {icon}
    <span className="text-xs">{label}</span>
  </button>
);

export default NavButton;