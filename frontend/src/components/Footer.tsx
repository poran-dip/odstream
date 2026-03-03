const Footer = () => {
  return (
    <footer className="mt-16 mb-8">
      <div className="w-full mx-auto backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl py-8 px-8 shadow-xl">
        <div className="text-center space-y-4">
          <p className="text-xl font-semibold text-gray-800 dark:text-white leading-relaxed">
            Work done at{" "}
            <span className="text-blue-600 dark:text-blue-400 font-bold">
              CORE Lab
            </span>
            ,
            <span className="text-purple-600 dark:text-purple-400">
              {" "}
              EEE Department
            </span>
            ,
            <span className="text-indigo-600 dark:text-indigo-400 font-bold">
              {" "}
              IIT Guwahati
            </span>
          </p>
          <div className="w-16 h-px bg-gradient-to-r from-blue-500 to-purple-500 mx-auto opacity-60"></div>
          <p className="text-lg text-gray-700 dark:text-gray-200 font-medium">
            Funded by:{" "}
            <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
              TIH IIT Guwahati
            </span>
          </p>
          <p className="text-base text-gray-600 dark:text-gray-300 italic leading-relaxed">
            <span className="font-medium">Developers:</span> Poran Dip Boruah,
            Md Ruhan Roushan Islam, Pooja Basumatary
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
