#hide.
%%action.
#show selected(X).
%%roles.
{% for action in actions %}
	{% for role in action.roles %}
		#show role_{{action.name}}_{{role.name}}(X).
	{% endfor %}
{% endfor %}
%%predications.
{% for action in actions %}
	{% for role in action.roles %}
		{% for precondition in role.preconditions %}
			#show {{precondition.method}}(X,bl).
		{% endfor %}
	{% endfor %}
{% endfor %}	
{% block schedules %}
	{% block actions_list %}
		{% for action in actions %}
			action(action_{{action.name}}).
		{% endfor %}
		%% there must be one selected action
		1 { selected(A) : action(A) } 1.
	{% endblock actions_list %}
	{% block actions_implementation %}
		{% for action in actions %}
			%% {{ action.name}} %%%%%%%%%%%%%%%%%%%%%%%%
			%% there must be {{action.roles|length}} devices.
			{% for role in action.roles %}
				role_{{action.name}}_{{role.name}}_device(D) :- {% for interface in role.interfaces %}device_{{ interface }}(D){% if not forloop.last %}, {% endif %}{% endfor %}.
				1 { role_{{action.name}}_{{ role.name }}(D) : role_{{action.name}}_{{role.name}}_device(D) } 1 :- selected(action_{{ action.name }}).	
			{% endfor %}
            %% all of the roles must be assigned to different devices
            {% for pair in action.constr %}
                :-{% for dev in pair %}role_{{action.name}}_{{dev}}(D), role_{{action.name}}_{{dev}}_device(D){% if not forloop.last %}, {% endif %}{% endfor %}.
            {% endfor %}
			%% predications%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			{% for role in action.roles %}
				{% for precondition in role.preconditions %}
					{{precondition.method}}(X,{{precondition.value}}) :- role_{{action.name}}_{{role.name}}(X), device_{{precondition.interface}}(X), selected(action_{{action.name}}).
					{% if precondition.value %}
						:- {{precondition.method}}(X,false), role_{{action.name}}_{{role.name}}(X), device_{{precondition.interface}}(X), selected(action_{{action.name}}).
					{% else %}
						:- {{precondition.method}}(X,false), role_{{action.name}}_{{role.name}}(X), device_{{precondition.interface}}(X), selected(action_{{action.name}}).
					{% endif %}
					{{precondition.method}}(X,true) :- not {{precondition.method}}(X,false), device_{{precondition.interface}}(X).
					{{precondition.method}}(X,false) :- not {{precondition.method}}(X,true), device_{{precondition.interface}}(X).
				{% endfor %}
			{% endfor %}
		{% endfor %}
	{% endblock actions_implementation %}
{% endblock schedules %}
{% block devices %}
	{% for device in devices %}
		{% for interface in device.interfaces %}
			device_{{interface}}(id{{device.id}}).
		{% endfor %}
	{% endfor %}
{% endblock devices %}
