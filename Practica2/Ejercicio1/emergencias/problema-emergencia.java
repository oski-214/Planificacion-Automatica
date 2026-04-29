import JSHOP2.*;

public class problema-emergencia
{
	private static String[] defineConstants()
	{
		String[] problemConstants = new String[8];

		problemConstants[0] = "d1";
		problemConstants[1] = "loc-base";
		problemConstants[2] = "g1";
		problemConstants[3] = "b1";
		problemConstants[4] = "loc-almacen";
		problemConstants[5] = "medicina";
		problemConstants[6] = "juan";
		problemConstants[7] = "loc-hospital";

		return problemConstants;
	}

	private static void createState0(State s)	{
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(8), new TermList(TermConstant.getConstant(9), TermList.NIL))));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(10), TermList.NIL)));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(11), new TermList(TermConstant.getConstant(12), TermList.NIL))));
		s.add(new Predicate(5, 0, new TermList(TermConstant.getConstant(11), new TermList(TermConstant.getConstant(13), TermList.NIL))));
		s.add(new Predicate(4, 0, new TermList(TermConstant.getConstant(14), new TermList(TermConstant.getConstant(15), TermList.NIL))));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(14), new TermList(TermConstant.getConstant(13), TermList.NIL))));
	}

	public static void main(String[] args) throws InterruptedException
	{
		TermConstant.initialize(16);

		Domain d = new emergencias();

		d.setProblemConstants(defineConstants());

		State s = new State(8, d.getAxioms());

		JSHOP2.initialize(d, s);

		TaskList tl;
		Thread thread;

		createState0(s);

		tl = new TaskList(1, true);
		tl.subtasks[0] = new TaskList(new TaskAtom(new Predicate(1, 0, TermList.NIL), false, false));

		thread = new SolverThread(tl, 1);
		thread.start();
		while (thread.isAlive())
			Thread.sleep(500);
	}
}