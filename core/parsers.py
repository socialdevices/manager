import ast
import logging

logger = logging.getLogger(__name__)

def capitalize_first_letter(string):
    return string[0].capitalize() + string[1:]

BOOLOP_SYMBOLS = {
    ast.And:    'and',
    ast.Or:     'or'
}

CMPOP_SYMBOLS = {
    ast.Eq:     '==',
    ast.Gt:     '>',
    ast.GtE:    '>=',
    ast.In:     'in',
    ast.Is:     'is',
    ast.IsNot:  'is not',
    ast.Lt:     '<',
    ast.LtE:    '<=',
    ast.NotEq:  '!=',
    ast.NotIn:  'not in'
}

UNARYOP_SYMBOLS = {
    ast.Invert: '~',
    ast.Not:    'not',
    ast.UAdd:   '+',
    ast.USub:   '-'
}


class InterfaceParser(ast.NodeVisitor):

    def __init__(self):
        self.interface = {}

    def get_interface(self):
        return self.interface

    def _continue_visit(self, node):
        super(InterfaceParser, self).generic_visit(node)

    def parse(self, code):
        tree = ast.parse(code)
        self.visit(tree)

        return self.interface

    def visit_Module(self, node):
        # First, traverse classes that have a decorator named deviceInterface
        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef):
                for decorator in stmt.decorator_list:
                    if decorator.id == 'deviceInterface':

                        # Raise exception, if more than one interface is found
                        if not self.interface:
                            self.visit(stmt)
                        else:
                            raise InterfaceParseError('Multiple interface classes with decorator @deviceInterface have been defined.')

        # Raise exception, if no interfaces were found
        if not self.interface:
            raise InterfaceParseError('Interface decorator @deviceInterface is missing.')

        # Raise exception, if no precondition methods were found
        if not self.interface['precondition_methods']:
            raise InterfaceParseError('Interface %s does not have any precondition methods defined with decorator @precondition.' % self.interface['interface_name'])

        # After that, traverse classes that have a base class named TriggeringEvent
        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef):
                for base in stmt.bases:
                    if base.id == 'TriggeringEvent':
                        self.visit(stmt)

        # Raise exception, if no trigger method classes have been defined
        if not self.interface['trigger_methods']:
            raise InterfaceParseError('No trigger method class with base class TriggeringEvent has been defined.')

    def visit_ClassDef(self, node):

        # Only traverse the children of the node, if the class is an interface class
        for decorator in node.decorator_list:
            if decorator.id == 'deviceInterface':
                self.interface = {'interface_name': node.name, 'precondition_methods': [], 'trigger_methods': []}

                self._continue_visit(node)

        # Only traverse the children of the node, if the class is a trigger class
        for base in node.bases:
            if base.id == 'TriggeringEvent':
                trigger_method = node.name[0].lower() + node.name[1:]

                # Add the trigger method, if a precondition method with the same name exists
                # The method name could also be a key.. then no loop would be necessary
                for method in self.interface['precondition_methods']:
                    if trigger_method == method['method_name']:
                        if not trigger_method in self.interface['trigger_methods']:
                            self.interface['trigger_methods'].append(trigger_method)
                        # Raise exception, if a duplicate trigger method class has been defined
                        else:
                            raise InterfaceParseError('Duplicate trigger method class %s.' % node.name)

                # If no method in the interface matches the trigger method, raise an exception
                if not self.interface['trigger_methods']:
                    raise InterfaceParseError('The name of the trigger method class %s does not match any of the precondition methods defined in interface %s.' % (node.name, self.interface['interface_name']))

    def visit_FunctionDef(self, node):
        # Add those methods that have a decorator named precondition to the precondition method list
        for decorator in node.decorator_list:
            if decorator.id == 'precondition':
                precondition_method = {'method_name': node.name, 'parameters': []}

                for argument in node.args.args:
                    if argument.id != 'self':
                        if not argument.id in precondition_method['parameters']:
                            precondition_method['parameters'].append(argument.id)
                        # Raise exception, if a precondition method contains a duplicate parameter
                        else:
                            raise InterfaceParseError('Duplicate parameter %s for precondition method %s in interface %s.' % (argument.id, node.name, self.interface['interface_name']))

                # Raise exception, if the precondition method is a duplicate
                for method in self.interface['precondition_methods']:
                    if method['method_name'] == node.name:
                        raise InterfaceParseError('Duplicate precondition method %s.' % node.name)

                self.interface['precondition_methods'].append(precondition_method)


class InterfaceParseError(Exception):
    """Base class for interface parse errors."""
    pass


class ActionParser(ast.NodeVisitor):

    def __init__(self):
        self.action = {}
        self.action_parameters = []
        self.precondition_expression = []
        self.in_return = False
        self.parse_interfaces = False
        self.parse_expression = False

    def get_action(self):
        return self.action

    def _continue_visit(self, node):
        super(ActionParser, self).generic_visit(node)

    def parse(self, code):
        tree = ast.parse(code)
        self.visit(tree)

        return self.action

    def visit_Module(self, node):
        # Only traverse classes that have a base class named Action
        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef):
                for base in stmt.bases:
                    if base.id == 'Action':
                        # Raise exception, if more than one action is found
                        if not self.action:
                            self.visit(stmt)
                        else:
                            raise ActionParseError('Multiple action classes with base class Action have been defined.')

        # Raise exception, if no actions were found
        if not self.action:
            raise ActionParseError('No action class with base class Action has been defined.')

    def visit_ClassDef(self, node):
        # Only traverse the node, if the class is an action class
        for base in node.bases:
            if base.id == 'Action':
                self.action = {'action_name': node.name,
                               'precondition_expression': '',
                               'precondition_replacements': [],
                               'devices': {},
                               'parameters': []}
                self.precondition_expression = []

                # Traverse the precondition method of the action class
                has_action_precondition = False
                for stmt in node.body:
                    if isinstance(stmt, ast.FunctionDef):
                        for decorator in stmt.decorator_list:
                            if decorator.id == 'actionprecondition':
                                has_action_precondition = True
                                self.visit(stmt)

                # Raise exception, if the action does not have an action precondition
                if not has_action_precondition:
                    raise ActionParseError('No method with decorator @actionprecondition has been defined for action class %s.' % node.name)

                self.action['precondition_expression'] = ''.join(self.precondition_expression)

                # Raise exception, if the return statement does not contain a valid boolean
                # precondition expression
                if self.action['precondition_expression'] == '()':
                    raise ActionParseError('The return statement of the precondition method in class %s does not contain a valid boolean precondition expression consisting of precondition methods.' % node.name)

                # Get the action parameters that are not roles
                for parameter_name in self.action_parameters:
                    if parameter_name not in self.action['devices']:
                        parameter = {'name': '', 'position': ''}
                        parameter['name'] = parameter_name
                        parameter['position'] = self.action_parameters.index(parameter_name)
                        self.action['parameters'].append(parameter)

    def visit_FunctionDef(self, node):
        # Traverse the method, if it has an @actionprecondition decorator
        for decorator in node.decorator_list:
            if decorator.id == 'actionprecondition':
                # First, store the parameters of the action precondition method
                for argument in node.args.args:
                    if argument.id != 'self':
                        if not argument.id in self.action_parameters:
                            self.action_parameters.append(argument.id)
                        # Raise exception, if a parameter is a duplicate
                        else:
                            raise ActionParseError('Duplicate parameter %s for precondition method %s.' % (argument.id, node.name))

                # Raise exception, if the action precondition does not have any parameters
                if not self.action_parameters:
                    raise ActionParseError('Precondition method %s does not have any parameters.' % node.name)

                # After that, only traverse the return statement
                has_return_statement = False
                for stmt in node.body:
                    if isinstance(stmt, ast.Return):
                        has_return_statement = True
                        self.in_return = True
                        self.visit(stmt)
                        self.in_return = False

                # Raise exception, if the action precondition does not have a return statement
                if not has_return_statement:
                    raise ActionParseError('The precondition method %s does not have a return statement.' % node.name)

    def visit_Return(self, node):
        if self.in_return:
            # Raise exception, if the return statement does not contain a boolean expression
            if not isinstance(node.value, ast.BoolOp):
                raise ActionParseError('The return statement in the precondition method does not contain a boolean expression.')

            # First, traverse the interface declarations
            self.parse_interfaces = True
            self._continue_visit(node)
            self.parse_interfaces = False

            # Raise exception, if no action device interfaces have been declared in the
            # return statement
            if not self.action['devices']:
                raise ActionParseError('Method hasInterface() has not been called in the return statement of the precondition method.')

            # After that, form the boolean expression
            self.parse_expression = True
            self._continue_visit(node)
            self.parse_expression = False

    def visit_BoolOp(self, node):
        if self.in_return:

            # Traverse the interface declarations, if parse_interfaces is True
            if self.parse_interfaces:
                for value in node.values:
                    if isinstance(value, ast.Call):
                        if value.func.attr == 'hasInterface':
                            self.visit(value)
                    # The boolean expression in the return statement can consist of several
                    # nested boolean expressions.
                    elif isinstance(value, ast.BoolOp):
                        self.visit(value)
                    # Raise exception, if a value in the return statement is other than
                    # a function call or a boolean expression
                    else:
                        raise ActionParseError('The boolean expression in the return statement of the action precondition method can only consist of function calls or nested boolean expressions.')

            # Form the boolean expression, if parse_expression is True
            if self.parse_expression:
                self.precondition_expression.append('(')
                num_expressions = 0
                for value in node.values:
                    # If the value is a precondition method of a device, then traverse it
                    if not isinstance(value, ast.Call) or (isinstance(value, ast.Call) and value.func.attr != 'hasInterface' and value.func.attr != 'proximity'):
                        if num_expressions:
                            self.precondition_expression.append(' %s ' % BOOLOP_SYMBOLS[type(node.op)])
                        self.visit(value)
                        num_expressions += 1
                    # The boolean expression can consist of other boolean expressions
                    else:
                        self.visit(value)
                self.precondition_expression.append(')')

    def visit_Call(self, node):
        if self.in_return:
            # Store the devices and the interfaces of the devices
            if self.parse_interfaces and node.func.attr == 'hasInterface':
                if isinstance(node.func.value, ast.Name):
                    device = node.func.value.id

                    # Check that the device is declared in the parameters of the action precondition method
                    if device in self.action_parameters:
                        interface = node.args[0].id
                        if not device in self.action['devices']:
                            self.action['devices'][device] = {'interfaces': [interface], 'parameter_position': self.action_parameters.index(device)}
                        else:
                            if not interface in self.action['devices'][device]['interfaces']:
                                self.action['devices'][device]['interfaces'].append(interface)
                            # Raise exception, if the interface has already been declared for the device
                            else:
                                raise ActionParseError('Method hasInterface(\'%s\') called multiple times for action device %s.' % (interface, device))
                    # Raise exception, if the device has not been declared in the precondition parameters
                    else:
                        raise ActionParseError('Device %s is not declared in the precondition parameters.' % device)

            # Store the precondition methods
            if self.parse_expression and node.func.attr != 'proximity' and node.func.attr != 'hasInterface':
                if isinstance(node.func.value, ast.Attribute) and isinstance(node.func.value.value, ast.Name):
                    device = node.func.value.value.id

                    # Check that the device is declared as a parameter of the action precondition method
                    if device in self.action_parameters and device in self.action['devices']:
                        method = node.func.attr
                        interface = capitalize_first_letter(node.func.value.attr)

                        if interface in self.action['devices'][device]['interfaces']:
                            self.action['precondition_replacements'].append({'device': device, 'interface': interface, 'method': method})
                            self.precondition_expression.append('?')
                        # Raise exception, if the interface has not been declared for the device
                        else:
                            raise ActionParseError('Interface %s has not been declared for device %s with method hasInterface().' % (interface, device))
                    # Raise exception, if the device is not declared in the parameters
                    elif not device in self.action_parameters:
                        raise ActionParseError('Device %s is not declared in the precondition parameters.' % device)
                    elif not device in self.action['devices']:
                        raise ActionParseError('No interfaces have been declared for device %s with method hasInterface().' % device)
                # Raise exception, if the format of the precondition method is incorrect
                else:
                    raise ActionParseError('The format of the precondition method call is incorrect (line %s, col %s): %s. The format should be <device>.<interface>.<precondition_method>.' % (node.lineno, node.col_offset, node.func.attr))

    def visit_Compare(self, node):
        if self.in_return:
            self.precondition_expression.append('(')

            # Left comparison operand
            if isinstance(node.left, ast.Name):
                self.precondition_expression.append(node.left.id)
            elif isinstance(node.left, ast.Num):
                self.precondition_expression.append(str(node.left.n))
            else:
                self.visit(node.left)

            self.precondition_expression.append(' %s ' % CMPOP_SYMBOLS[type(node.ops[0])])

            # Right comparison operand
            if isinstance(node.comparators[0], ast.Name):
                self.precondition_expression.append(node.comparators[0].id)
            elif isinstance(node.comparators[0], ast.Num):
                self.precondition_expression.append(str(node.comparators[0].n))
            else:
                self.visit(node.comparators[0])

            self.precondition_expression.append(')')
        else:
            self._continue_visit(node)

    def visit_UnaryOp(self, node):
        if self.in_return:
            self.precondition_expression.append('(')
            op = UNARYOP_SYMBOLS[type(node.op)]
            self.precondition_expression.append(op)
            if op == 'not':
                self.precondition_expression.append(' ')

            self.visit(node.operand)
            self.precondition_expression.append(')')


class ActionParseError(Exception):
    """Base class for action parse errors."""
    pass


class ScheduleParser(ast.NodeVisitor):

    def __init__(self):
        self.schedule = {}
        self.trigger_from_variable_name = None
        self.action_list_variable_names = []
        self.in_schedule = False
        self.in_action = False
        self.in_main = False

    def get_schedule(self):
        return self.schedule

    def _continue_visit(self, node):
        super(ScheduleParser, self).generic_visit(node)

    def parse(self, code):
        tree = ast.parse(code)
        self.visit(tree)

        return self.schedule

    def visit_Module(self, node):
        # First, parse all the information related to the schedule
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                for decorator in stmt.decorator_list:
                    if decorator.id == 'schedulingFunction':
                        self.in_schedule = True
                        self.visit(stmt)
                        self.in_schedule = False

        # Raise exception, if no schedules were found
        if not self.schedule:
            raise ScheduleParseError('No schedule function with decorator @schedulingFunction has been defined.')

        # Raise exception, if no schedule actions were found
        if not self.schedule['actions']:
            raise ScheduleParseError('The schedule function does not contain any actions.')

        # After that, parse the trigger method from __main__
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                if isinstance(stmt.test, ast.Compare):
                    if stmt.test.left.id == '__name__' and stmt.test.comparators[0].s == '__main__':
                        self.in_main = True
                        self.visit(stmt)
                        self.in_main = False

        # Raise exception, if no trigger method was found
        if not self.schedule['trigger_method']:
            raise ScheduleParseError('No trigger method defined for the schedule with scheduling.addSchedule() in __main__.')

        # Finally, parse the trigger method's interface
        for stmt in node.body:
            if isinstance(stmt, ast.ImportFrom):
                for alias in stmt.names:
                    name = alias.name[0].lower() + alias.name[1:]
                    if name == self.schedule['trigger_method']:
                        modules = stmt.module.split('.')
                        interface = capitalize_first_letter(modules.pop())
                        self.schedule['trigger_interface'] = interface

        # Raise exception, if the trigger method's interface was not found
        if not self.schedule['trigger_interface']:
            raise ScheduleParseError('The trigger method has not been imported from an interface module.')

    def visit_FunctionDef(self, node):
        # Only traverse the children of the node, if the function is a scheduling function
        for decorator in node.decorator_list:
            if decorator.id == 'schedulingFunction':
                self.schedule = {'schedule_name': node.name, 'actions': [], 'trigger_interface': '', 'trigger_method': ''}

                # First, parse the action variables in the list in the return statement
                has_return_statement = False
                for stmt in node.body:
                    if isinstance(stmt, ast.Return):
                        has_return_statement = True
                        self.visit(stmt)

                # Raise exception, if the schedule function does not have a return statement
                if not has_return_statement:
                    raise ScheduleParseError('The schedule function %s does not have a return statement.' % node.name)

                # After that, parse everything else
                for stmt in node.body:
                    if not isinstance(stmt, ast.Return):
                        self.visit(stmt)

    def visit_Return(self, node):
        if self.in_schedule:
            # Store the variable names of the actions in the list
            # Could return an exception, if not a list
            if isinstance(node.value, ast.List):
                for value in node.value.elts:
                    if isinstance(value, ast.Name):
                        self.action_list_variable_names.append(value.id)
                    # Raise exception, if the list does not contain variable names
                    else:
                        raise ScheduleParseError('The list in the return statement of the schedule function does not have variable names as list members.')
            # Raise exception, if the return statement does not contain a list
            else:
                raise ScheduleParseError('The return statement of the schedule function does not contain a list.')

    def visit_Assign(self, node):
        if self.in_schedule:
            # Store the name of the variable holding the "trigger from" information
            if isinstance(node.value, ast.Attribute):
                if node.value.value.id == 'triggeringEvent' and node.value.attr == 'messFrom':
                    self.trigger_from_variable_name = node.targets[0].id
            # Store the actions
            elif isinstance(node.value, ast.Call):
                if node.targets[0].id in self.action_list_variable_names:
                    self.in_action = True
                    self.visit(node.value)
                    self.in_action = False

    def visit_Call(self, node):
        if self.in_action:
            # Raise exception, if the schedule contains a duplicate action
            for action in self.schedule['actions']:
                if action['action_name'] == node.func.id:
                    raise ScheduleParseError('Duplicate schedule action %s.' % node.func.id)

            action = {'action_name': node.func.id, 'trigger_from': None}

            # Loop through the action arguments and store the position of "trigger from"
            for i, argument in enumerate(node.args):
                if isinstance(argument, ast.Name):
                    if argument.id == self.trigger_from_variable_name:
                        action['trigger_from'] = i
            self.schedule['actions'].append(action)

        if self.in_main:
            if isinstance(node.func, ast.Attribute):
                if node.func.value.id == 'scheduling' and node.func.attr == 'addSchedule':
                    # Store the precondition method that is the trigger for the schedule
                    if self.schedule['schedule_name'] == node.args[1].id:
                        trigger_method = node.args[0].id[0].lower() + node.args[0].id[1:]
                        self.schedule['trigger_method'] = trigger_method


class ScheduleParseError(Exception):
    """Base class for schedule parse errors."""
    pass
    
