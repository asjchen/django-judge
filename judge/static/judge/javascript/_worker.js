var output = "";

function run_test( f, args ) {
	start = Date.now();
	output = f.apply(null, args).toString();
	stop = Date.now();
	diff = stop - start;
	return diff;
}

onmessage = function ( e ) {
	data = e.data;
	switch (data.cmd) 
	{
		case 'run_test':
			var func_string, test_func, time, error = false;
			func_string = "function foo(" + data.function_vars + ") { " + data.function_body + ";} foo;";
			test_func = eval(func_string);
			try {
				runtime = run_test( test_func, data.function_args );
			} catch (e) {
				error = e.message;
			}

			if ( error ) 
			{
				var msg_to_parent = {
					'runstatus': 'error',
					'message': error
				};
			
			} 
			else 
			{
				var msg_to_parent = {
					'runstatus': 'success',
					'runtime': runtime,
					'output': output
				};
			}
			postMessage(msg_to_parent);
			break;
		default:
			postMessage("bad command");
	}
}