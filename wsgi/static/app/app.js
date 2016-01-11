$(function(){

	var $template = $('#table-notes-tmpl'),	
		$selectNotebook = $('#select-notebook'),
		$selectRepo = $('#select-repo'),
		$btnPublish = $('#btn-publish'),	
		$btnSelectAll = $('#btn-select-all'),
		$ckbSelectAll = $('#ckb-select-all'),
		$ajaxnotifier = $('#div-ajax-notifier'),
		/**
		  * @breif  A simple wrapper for artTemplate template func.
		  * @param  template_selector, the render template selector
		  * @param  parent_selector, the parent elem to append the template content
		  * @param  data, the data object to render in template
		  * @retval None
		  */
		$fnTemplateHelper = function(template_selector, parent_selector, data){
			var html = template(template_selector, {list: data});
			$(parent_selector).html(html);
		},
		/**
		  * @breif  Start publishing
		  * @param  None
		  * @retval None
		  */
		$fnPublish = function(){
			var url = '/sync/'
			$fnWidgetStatusSet(true); // disable the publish button
			data = {};
			$('input[data-note-id]:checked').each(function(index, elem){
				var note_guid = $(this).data('note-id');
				data['note_guid'] = $(this).data('note-id');                                      // Note GUID
				data['title'] = $('input[data-title-id=' + $(this).data('note-id') + ']').val();  // Markdown file name
				data['repo'] = $selectRepo.val();                                                 // Repo 
				data['message'] = 'Jekynote synchornize';                                         // Commit message

				$(document).queue(function(){
					$ajaxnotifier.ajaxNotifier();	
					$ajaxnotifier.ajaxNotifier('call', {
						url: url,
						type: 'POST',
						data: data,
						success: function(data){
							if(data.rc == 0)
								$('#status-' + note_guid).html("<i class='uk-icon-check-circle'></i>");
							else
								$('#status-' + note_guid).html("<i class='uk-icon-times-circle'></i>");							
						},
						error: function(data){
							$('#status-' + note_guid).html("<i class='uk-icon-times-circle'></i>");
						},
						complete: function(){
							$(document).dequeue();
						}
					});
				});

				// Append a task after the last elem
				if(index == $('input[data-note-id]:checked').length - 1){
					$(document).queue($fnWidgetStatusSet); // Enable the widget
				}
			});

			$(document).dequeue();
		}
		/**
		  * @breif  Select and de-select all note function
		  * @param  None
		  * @retval None
		  */
		$fnCheckUncheckAll = function(){
			$('input[data-note-id]').prop('checked', $ckbSelectAll.prop('checked'));
		}
		/**
		  * @breif  Get all the notebooks for current user
		  * @param  None
		  * @retval None
		  */
		$fnGetNoteBooks = function(){		
			var url = "/notebooks/";
			$ajaxnotifier.ajaxNotifier();	
			$ajaxnotifier.ajaxNotifier('call', {
				url: url,
				success: function(data){
					$fnTemplateHelper('notebooks-tmpl', '#select-notebook', data);
					UIkit.formSelect('#form-select-notebooks').init();
					$(document).dequeue();
				}
			});
		},
		/**
		  * @brief  SetUp event listener
		  * @param  None
		  * @retval None
		  */
		$fnEventBinding = function(){
			/* notebook select widget changed */
			$selectNotebook.change(function(){
				$fnGetNote($(this).val());
			});	

			/* select all note */
			$ckbSelectAll.change($fnCheckUncheckAll);

			/* Publish button */
			$btnPublish.click($fnPublish);

			/* trigger next step */
			$(document).dequeue();
		},
		/**
		  * @brief  Widget Status set function
		  * @param  disabled set the button disabled or not.
		  * @retval None
		  */
		$fnWidgetStatusSet = function(disabled){
			var flag = (typeof disabled == 'boolean' ? disabled : false);
			$btnPublish.prop('disabled', flag);
			$btnSelectAll.prop('disabled', flag);
		}
		/**
		  * @breif  Get notes with specific notebook GUID
		  * @param  Evernote notebook GUID
		  * @retval None
		  */
		$fnGetNote = function(){
			var notebook = $('#select-notebook').val();
			if(notebook){
				$fnWidgetStatusSet(true);
				$ajaxnotifier.ajaxNotifier();
				var url = "/notebooks/{0}/notes/".replace('{0}', notebook);	
				$ajaxnotifier.ajaxNotifier('call', {
					url: url,
					success: function(data){
						$fnTemplateHelper('table-notes-tmpl', '#table-notes', data);
						$(document).dequeue();
						$fnWidgetStatusSet(false);
					}
				});
			}
		},
		/**
		  * @breif  Get github repo with user token
		  * @param  None
		  * @retval None
		  */
		$fnGetGitRepo = function(){
			var url = "/github-repo/"
			$ajaxnotifier.ajaxNotifier();
			$ajaxnotifier.ajaxNotifier('call', {
				url: url,
				success: function(data){
					$fnTemplateHelper('repo-tmpl', '#select-repo', data);
					UIkit.formSelect('#form-select-repo').init();
					$(document).dequeue();
				},
				complete: function(data){
				}
			});
		},
		$fnDateFormat = function(timestamp, format){
		    date = new Date(timestamp);

		    var map = {
		        "M": date.getMonth() + 1, //月份 
		        "d": date.getDate(), //日 
		        "h": date.getHours(), //小时 
		        "m": date.getMinutes(), //分 
		        "s": date.getSeconds(), //秒 
		        "q": Math.floor((date.getMonth() + 3) / 3), //季度 
		        "S": date.getMilliseconds() //毫秒 
		    };
		    format = format.replace(/([yMdhmsqS])+/g, function(all, t){
		        var v = map[t];
		        if(v !== undefined){
		            if(all.length > 1){
		                v = '0' + v;
		                v = v.substr(v.length-2);
		            }
		            return v;
		        }
		        else if(t === 'y'){
		            return (date.getFullYear() + '').substr(4 - all.length);
		        }
		        return all;
		    });
		    return format;
		};

	// Register dateFormat helper
	template.helper('dateFormat', $fnDateFormat);	

	// Init flow begin
	$(document).queue($fnGetGitRepo);
	$(document).queue($fnGetNoteBooks);
	$(document).queue($fnGetNote);	
	$(document).queue($fnEventBinding);
	$(document).queue($fnWidgetStatusSet);

	//$(document).dequeue();
});
