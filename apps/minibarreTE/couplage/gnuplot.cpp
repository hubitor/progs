
#include "gnuplot.h"


Gnuplot::Gnuplot() 
{
	// with -persist option you will see the windows as your program ends
	//gnuplotpipe=_popen("gnuplot -persist","w");
	//without that option you will not see the window

	// because I choose the terminal to output files so I don't want to see the window

	//gnuplotpipe=_popen("gnuplot","w");
	gnuplotpipe=popen("gnuplot","w");

	if (!gnuplotpipe) 
	{
		std::cerr << "Gnuplot not found !"; 
	}
}

Gnuplot::~Gnuplot() 
{
	fprintf(gnuplotpipe,"exit\n");
	//_pclose(gnuplotpipe);
	pclose(gnuplotpipe);
}

void 
Gnuplot::operator()(const std::string & command) 
{
	fprintf(gnuplotpipe,"%s\n",command.c_str());
	fflush(gnuplotpipe);
	// flush is necessary, nothing gets plotted else
};

