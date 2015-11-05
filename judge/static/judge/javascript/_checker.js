// This script uses web workers to run and time the user's code submission. If the code executes for more than 5000
// milliseconds, then the code should cease running and the script should send a timeout message.

var worker = new Worker(tester_url);
var output = "";

function stop_time()
{
	worker.terminate();
	if ( output === "" ) 
	{
		alert('Submission Timed Out');
	}
}

worker.addEventListener('message', function(msg) {
	if (msg.data.runstatus === 'success' ) {

		// send ajax request, see if msg.data.output is same, then return boolean value
		guess = {
			'output': msg.data.output,
			'csrfmiddlewaretoken': csrf
		};
		function compare(info, textstatus, req)
		{
			if ( info['same'] )
			{
				output = msg.data.output;
				data = {
					'runtime': msg.data.runtime,
					'submitter': user,
					'source': function_body,
					'csrfmiddlewaretoken': csrf
				};
				function success(info, textstatus, req)
				{
					if ( info['score'] >= 0 ) location.assign(leaderboard_url + info['entry_id'] + '/');
				}
				$.post( post_url, data, success );
			}
			else
			{
				alert('Answer Incorrect');
				location.assign(leaderboard_url);
			}
		}
		$.post( compare_url, guess, compare );
	} 
	else if (msg.data.runstatus === 'error' ) 
	{
		alert('Error: ' + msg.data.message );
		location.assign(leaderboard_url);
	}
}, false);

var msg_to_worker = {
	'cmd': 'run_test',
	'function_body': function_body,
	'function_vars': function_vars,
	'function_args': function_args
};
worker.postMessage(msg_to_worker);
var timeoutID = setTimeout(stop_time, 5000);


