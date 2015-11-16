(function($){

	var methods = {
		init: function(options){
			var info = (options && 'info' in options? options.info : "<i class='uk-icon-spinner uk-icon-spin'></i> Loading...");
			var error = (options && 'error' in options? options.error : "<i class='uk-icon-exclamation-circle'></i> We have encounterred error, please try later.");
			$(this).data('info', info);
			$(this).data('error', error);
		},
		info: function(message){
			$(this).data('info', message);
		},
		error: function(message){
			$(this).data('error', message);
		},
		call: function(options){
			var info = $(this).data('info'),
			    error = $(this).data('error');

			var notifier = UIkit.notify(info, {timeout: 60000});
			
			$.ajax(options)
				.done(function(){
					notifier.close();
				})
				.fail(function(){
					notifier.content(error);
					notifier.status('danger')
				});
		}
	};

	$.fn.ajaxNotifier = function(methodOrOptions){
		if(methods[methodOrOptions]){
			return methods[methodOrOptions].apply(this, Array.prototype.slice.call(arguments, 1));
		} else if(typeof methodOrOptions == 'object' || !methodOrOptions) {
			// init
			return methods.init.apply(this, arguments);
		} else {
			$.error('Method ' + methodOrOptions + ' does not exist in jQuery.ajaxNotifier');
		}
	}
})(jQuery);